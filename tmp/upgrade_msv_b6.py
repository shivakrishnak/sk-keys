#!/usr/bin/env python3
"""Upgrade MSV-056 through MSV-065 from v2.1 to v3.0."""
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
    "MSV-056 - Feature Flags (Microservices).md",
    evo=(
        "Feature flags (feature toggles) were first documented as a pattern "
        "by Martin Fowler ('Feature Toggle', 2010) and elaborated by Pete "
        "Hodgson. The practice predated the documentation - teams used "
        "environment variables and database flags to control feature "
        "availability. LaunchDarkly (2014) and Unleash (open-source, 2015) "
        "created dedicated feature flag services. 'Progressive delivery' "
        "(James Governor, 2018) combined feature flags with canary deployments "
        "for safer, measurable rollouts. The discipline evolved from 'manual "
        "database toggle per service' to 'centralised flag management with "
        "targeting, analytics, and planned expiry.'"
    ),
    tw_principle=(
        "Feature flags separate deployment from release. Deploying code and "
        "releasing it to users are two distinct operations. Deploying puts "
        "code into production behind a disabled flag. Releasing turns on "
        "the flag for users. This separation enables: deploy at any time, "
        "release on a schedule, instant rollback by disabling the flag, and "
        "targeted release to specific users or percentages."
    ),
    tw_bullets=(
        "- **A/B testing:** A feature flag routing 50% of users to a new "
        "UI variant is A/B testing - same mechanism as progressive rollout, "
        "different purpose (measurement vs deployment safety).\n"
        "- **Kill switches:** A kill switch that disables a feature "
        "immediately in production is a feature flag with a binary state "
        "- used for emergency incident response.\n"
        "- **Dark launches:** Running new code in production without showing "
        "results to users (to test performance and correctness) is a feature "
        "flag in shadow mode - same mechanism, different usage."
    ),
    st=(
        "Feature flags accumulate at a rate companies consistently "
        "underestimate. Netflix had over 1,000 active feature flags in 2016. "
        "The danger is not the flags themselves but the technical debt they "
        "create: code with many if/else branches based on flag state becomes "
        "hard to reason about and test. Each flag adds at least two code paths "
        "to test. The correct practice is to treat every feature flag as having "
        "a planned expiry date: create a JIRA ticket to remove the flag at "
        "the same time you create the flag itself."
    ),
    q1_hint=(
        "Think about what the risk is: the new engineer correctly removed the "
        "flag code (the old flow is intentionally dead). But a regression test "
        "suite was written against the old spec and tests the old flow. Three "
        "weeks later, the tests find the old endpoint missing - which is "
        "correct behavior (it should be gone). The risk is that the regression "
        "tests are validating behavior that no longer exists, potentially masking "
        "whether the new flow is being correctly tested. The process fix: flag "
        "removal should include a mandatory review of all tests that reference "
        "the flag or the flag-controlled behavior, ensuring tests cover only "
        "the surviving code path."
    ),
    q2_hint=(
        "Think about what 'consistent flag state across all 20 services' "
        "means: if Service A evaluates the flag as ON and calls Service B "
        "which evaluates it as OFF, the pricing engine will produce "
        "inconsistent results (A uses new pricing, B uses old pricing). The "
        "solution: evaluate the flag state ONCE at the entry point "
        "(API gateway or first service in the chain) and pass the evaluated "
        "result as a request context header to all downstream services. "
        "Downstream services use the pre-evaluated state from the header "
        "rather than re-evaluating the flag independently."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your team has accumulated 300 active "
        "feature flags over 2 years. Engineers are afraid to remove flags "
        "because they don't know if they're still in use. An audit finds 60% "
        "have been at 100% rollout for more than 6 months. Design the "
        "feature flag lifecycle management process that prevents accumulation."
    ),
    q3_hint=(
        "Think about what 'planned flag removal' means as a process: every "
        "flag has a documented owner, a planned removal date, and a tracking "
        "ticket created at the same time as the flag. At 100% rollout, "
        "automatically create a removal ticket with a 30-day deadline. Explore "
        "whether a flag dashboard (shows flags by age, rollout %, last "
        "evaluation date) provides the visibility needed for teams to proactively "
        "clean up stale flags, and whether a linting rule that fails CI when "
        "a flag has been at 100% for more than 60 days enforces removal "
        "without relying on manual process."
    ),
)

upgrade(
    "MSV-057 - Graceful Shutdown (Microservices).md",
    evo=(
        "Graceful shutdown became a critical operational concern as container-"
        "based deployments made service restarts routine. In traditional VM "
        "deployments, services were rarely restarted (uptime was a virtue). "
        "Kubernetes' rolling deployments made pod restarts a frequent, "
        "expected event. The SIGTERM/SIGKILL lifecycle was defined in "
        "Kubernetes 1.0 (2015). Spring Boot's @PreDestroy hooks and Quarkus's "
        "fast startup became standard Java implementations. The discipline "
        "evolved from 'protect my long-running process' to 'design for "
        "graceful, fast shutdown as a normal daily operation.'"
    ),
    tw_principle=(
        "A service that cannot be gracefully stopped cannot be safely deployed. "
        "Graceful shutdown is not just about completing in-flight requests - "
        "it is about transitioning all service state (database transactions, "
        "message processing, scheduled tasks) to a clean, consistent state "
        "before the process exits. The same principle governs database "
        "connection pool shutdown, Kafka consumer shutdown, and HTTP server "
        "shutdown: drain before disconnect."
    ),
    tw_bullets=(
        "- **Database connection pool shutdown:** HikariCP drains all "
        "connections (completes queries or rolls back transactions) before "
        "releasing the pool - graceful shutdown for database resources.\n"
        "- **Kafka consumer shutdown:** A consumer that commits its last offset "
        "before disconnecting prevents message reprocessing - graceful shutdown "
        "for message consumption.\n"
        "- **HTTP server shutdown:** Tomcat/Netty stops accepting new connections "
        "but completes in-flight requests before stopping the thread pool - "
        "graceful shutdown for HTTP serving."
    ),
    st=(
        "Kubernetes' graceful shutdown has a subtle race condition even "
        "experienced teams miss: when a pod receives SIGTERM, Kubernetes "
        "simultaneously removes the pod's IP from Service endpoints. But the "
        "endpoint update propagates through kube-proxy to all nodes with a "
        "delay of up to several seconds. During this window, other pods may "
        "still connect to the terminating pod's IP and receive connection "
        "refused errors. Setting a preStop sleep (5-10 seconds) gives endpoint "
        "propagation time to complete before the pod starts shutting down. "
        "Without this sleep, the graceful shutdown of the process is correct "
        "but in-flight requests from other pods still fail."
    ),
    q1_hint=(
        "Think about the timeline: SIGTERM at T=0. preStop hook (`sleep 5`) "
        "runs: T=0 to T=5. SIGTERM delivered to application at T=5. Application "
        "starts graceful shutdown: closes HTTP listener, waits for 3 active "
        "HTTP requests (2s remaining, done by T=7), waits for Kafka message "
        "(40ms, done by T=5.04), waits for DB transactions (1s each, done "
        "by T=6). All work completes by T=7. Container exits at T=7. "
        "`terminationGracePeriodSeconds=10`: no SIGKILL is issued. All work "
        "completes gracefully within the grace period."
    ),
    q2_hint=(
        "Think about what the actual requirement is: completing in-progress "
        "work, not waiting 10 minutes for no-ops. Options: (1) make batch "
        "imports resumable (checkpoint progress, restart from the last "
        "checkpoint after a restart); (2) move batch imports to a dedicated "
        "batch service with its own shutdown behavior, isolated from the main "
        "service; (3) design each import unit as a short-lived operation "
        "(process one record at a time, short-lived, easily restartable). "
        "Explore whether checkpointing reduces the worst-case shutdown window "
        "from 10 minutes to the time for one import unit (seconds to minutes)."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your service processes financial "
        "transactions. Graceful shutdown must guarantee: all in-flight HTTP "
        "requests complete, all open database transactions commit, and all "
        "Kafka messages being processed are either committed or returned to "
        "the queue. Design the shutdown sequence with zero duplicate "
        "transactions and zero lost transactions."
    ),
    q3_hint=(
        "Think about the order of shutdown operations: (1) stop accepting "
        "new HTTP requests (close the listener); (2) wait for all in-flight "
        "HTTP requests to complete; (3) for Kafka: commit the offset of the "
        "last successfully processed message OR rewind to the last committed "
        "offset if processing was not complete (preventing both message loss "
        "and duplicate processing); (4) commit or rollback all open database "
        "transactions; (5) close the database connection pool; (6) exit. "
        "Key ordering constraint: commit the database transaction BEFORE "
        "committing the Kafka offset, so that a crash between the two "
        "causes the message to be reprocessed (idempotent) rather than "
        "lost."
    ),
)

upgrade(
    "MSV-058 - Zero-Downtime Deployment.md",
    evo=(
        "Zero-downtime deployment became an industry goal as continuous "
        "delivery (Jez Humble and David Farley, 2010) pushed deployment "
        "frequency from monthly to daily to continuous. Traditional "
        "maintenance windows became incompatible with 24/7 global services. "
        "Rolling updates (Kubernetes' default), blue-green, and canary "
        "deployments all emerged as mechanisms for zero-downtime change. "
        "The discipline evolved from 'deploy during scheduled maintenance "
        "windows' to 'deployment is a daily operation that users should "
        "never notice.'"
    ),
    tw_principle=(
        "Zero-downtime deployment requires that old and new versions can run "
        "simultaneously during the transition. This constraint applies at every "
        "layer: the API must be backward compatible, the database schema must "
        "support both versions, and feature behavior must be consistent "
        "regardless of which version handles each request. Any layer that "
        "violates this makes the deployment not truly zero-downtime."
    ),
    tw_bullets=(
        "- **Expand-Contract database migration:** Old and new schema coexist "
        "during the migration window - zero-downtime applied to database "
        "schema changes.\n"
        "- **API versioning:** v1 and v2 coexist during the consumer migration "
        "window - zero-downtime applied to API evolution.\n"
        "- **Kubernetes rolling updates:** Multiple pod versions run "
        "simultaneously during a rolling update - the platform-level "
        "mechanism for zero-downtime deployments."
    ),
    st=(
        "Zero-downtime deployment is harder than teams expect because "
        "'downtime' has multiple definitions. A deployment can have zero HTTP "
        "500 errors (application-level uptime) while still having 5 seconds "
        "of elevated P99 latency during pod restarts (user-visible degradation). "
        "Teams that claim 'zero downtime' often mean 'no HTTP 500s during "
        "deployment' rather than the stricter definition of 'no user-observable "
        "degradation in any metric during deployment.' Both definitions matter, "
        "but they require different technical controls."
    ),
    q1_hint=(
        "Think about the situation: 3 pods on v2 (with the bug), 2 pods on "
        "v1 (correct). All pods pass readiness. Kubernetes won't auto-rollback "
        "(no readiness failure). Manual rollback: `kubectl rollout undo "
        "deployment/order-service` triggers a rolling update back to v1, "
        "replacing the 3 v2 pods. Affected orders: query the database for "
        "orders created during the v2 window with a discount calculation "
        "anomaly (the race condition affects 10% - look for orders with "
        "unexpectedly rounded or zero discount amounts created between the "
        "v2 deployment and rollback timestamps)."
    ),
    q2_hint=(
        "Think about what 'rename a field' requires for zero-downtime: the "
        "provider must return BOTH `orderDate` AND `createdAt` during the "
        "transition (same value, two field names). Deployment sequence: "
        "(1) deploy Order Service returning both fields; (2) each of the 12 "
        "downstream services migrates to use `createdAt` and deploys; "
        "(3) after all 12 consumers are migrated, deploy Order Service "
        "returning only `createdAt`; (4) remove the old field from OpenAPI "
        "spec. The transition window duration is set by the slowest of the "
        "12 consumer teams to complete their migration."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A new deployment changes the format of "
        "a JSON column from `{\"discount\": 10}` to "
        "`{\"discount\": {\"amount\": 10, \"type\": \"percentage\"}}`. "
        "Old pods crash with a parse error when reading new-format data "
        "written by new pods. Design the deployment sequence."
    ),
    q3_hint=(
        "Think about what Expand-Contract means for a JSON column format "
        "change: (1) Expand: deploy v2 pods that write the new format but "
        "ALSO support reading the old format (detect which format on read, "
        "handle both versions). At this point, both v1 and v2 pods can read "
        "both formats; (2) background job converts all existing data from "
        "old format to new format; (3) Contract: once all data is in new "
        "format and all pods are v2, remove the old-format reading code. "
        "The key: v2 must read both formats before v1 is removed from "
        "the cluster."
    ),
)

upgrade(
    "MSV-059 - Service Contract.md",
    evo=(
        "The concept of service contracts formalised as microservices replaced "
        "monoliths. In a monolith, contracts were enforced by the type system "
        "(changing a method signature caused a compile error). In microservices, "
        "interface changes caused runtime errors visible only in production. "
        "OpenAPI Specification (formerly Swagger, 2011) provided a machine-"
        "readable format for REST API contracts. gRPC Protocol Buffers (2015) "
        "provided strongly-typed contracts with backward compatibility rules. "
        "Consumer-Driven Contract Testing (Pact, 2013) added consumer "
        "expectations. The discipline evolved from 'document the API and hope "
        "consumers read it' to 'formally define, version, and test the contract "
        "from both sides.'"
    ),
    tw_principle=(
        "A service contract is an explicit promise about what a service will "
        "provide and what it will not change without notice. Without an explicit "
        "contract, every change is potentially breaking and every breaking "
        "change is invisible until it causes a production failure. Making the "
        "contract explicit (in code, in tests, in documentation) makes the "
        "implicit dependency explicit - which is the first step to "
        "managing it."
    ),
    tw_bullets=(
        "- **HTTP API contracts (OpenAPI):** An OpenAPI specification is a "
        "formal service contract for a REST API - explicit promises about "
        "endpoints, fields, and types.\n"
        "- **Message schema contracts:** An Avro or Protobuf schema is a "
        "service contract for a message - explicit promises about fields, "
        "types, and backward compatibility rules.\n"
        "- **Database schema as contract:** A database table schema is a "
        "service contract for data storage - explicit promises about columns, "
        "types, and constraints shared with dependent services."
    ),
    st=(
        "The most counterintuitive finding about service contracts is that "
        "having no contract often feels better than having one. Without a "
        "contract, every change is possible and teams feel productive. With "
        "a contract, every breaking change is flagged and API evolution "
        "requires coordination. This slowdown is exactly the right signal: "
        "it reveals the cost of change that was always there, previously "
        "invisible (manifesting as production incidents instead of CI failures). "
        "Teams that 'move fast' without contracts defer the cost of API "
        "evolution to production, where it is 10x more expensive."
    ),
    q1_hint=(
        "Think about what a contract means for a status code change: the "
        "Payment Service previously returned 200 with an error body for invalid "
        "amounts - this was the documented, contractual behavior. Changing to "
        "400 for the same input is a breaking change for consumers that check "
        "for 200 status and parse the body for success/failure. Semantically, "
        "400 is more correct HTTP. Contractually, it breaks consumers. The "
        "correct approach: version the API (v2 returns 400 for validation), "
        "maintain v1 with the old 200-for-everything behavior during "
        "migration, sunset v1 after all consumers migrate to v2."
    ),
    q2_hint=(
        "Think about how to discover what each consumer actually uses: "
        "(1) ask each team (fastest, incomplete); (2) review each consumer's "
        "code (accurate, time-consuming); (3) add API access logging that "
        "records which fields are accessed in responses (most accurate, "
        "requires instrumentation); (4) have each consumer write a Pact "
        "contract based on their actual usage (most rigorous - produces a "
        "machine-verifiable contract). The Pact approach is the most valuable "
        "retroactively: each team's Pact contract becomes the ongoing "
        "enforceable specification for what Order Service must not break."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** You provide an internal service with 30 "
        "consumers. A business requirement forces a semantic change: `ACTIVE` "
        "now means 'customer is active and premium' (previously 'customer is "
        "active'). 15 consumers use `status=ACTIVE` in their business logic. "
        "Design the contract change management process."
    ),
    q3_hint=(
        "Think about what 'semantic change without a field rename' means: "
        "changing what `ACTIVE` means is a silent breaking change - consumers "
        "checking `status=ACTIVE` will silently get different behavior without "
        "any code change on their part. The correct approach: add a new field "
        "`premium: boolean` for the new semantic, maintain `ACTIVE` with the "
        "original meaning for backward compatibility, deprecate the conflated "
        "meaning explicitly in the OpenAPI spec, and coordinate migration with "
        "the 15 affected teams with a defined sunset date."
    ),
)

upgrade(
    "MSV-060 - Backward Compatibility.md",
    evo=(
        "Backward compatibility became a formal engineering discipline as "
        "distributed systems made version coordination impractical. Protocol "
        "Buffers (Google, 2001, open-sourced 2008) introduced field numbers "
        "as an explicit mechanism for backward compatibility: new fields can "
        "be added without breaking old parsers (they ignore unknown field "
        "numbers). Avro (2009) and JSON Schema introduced compatibility "
        "rules for data serialisation. The Confluent Schema Registry (2015) "
        "made schema compatibility enforcement automated and CI-integrated. "
        "The discipline evolved from 'hope all consumers update simultaneously' "
        "to 'design schemas with explicit backward compatibility constraints "
        "enforced by tooling.'"
    ),
    tw_principle=(
        "Backward compatibility is a promise to consumers: 'You can upgrade "
        "the provider without changing your code.' This promise has strict "
        "technical implications: you can add optional fields (consumers ignore "
        "new fields), you cannot remove fields (consumers that read removed "
        "fields fail), and you cannot change field types (consumers that expect "
        "one type and receive another fail). Every API change must be "
        "categorized as backward compatible (additive) or breaking "
        "(requiring versioning and coordination)."
    ),
    tw_bullets=(
        "- **Database migration:** Adding a nullable column is backward "
        "compatible. Dropping a column is backward breaking. Same rules as "
        "API backward compatibility, applied to schema migration.\n"
        "- **Kafka message schema:** Adding an optional field to Avro is "
        "backward compatible. Removing a required field is backward breaking. "
        "The Confluent Schema Registry enforces these rules automatically.\n"
        "- **OS ABI stability:** Not removing syscalls and not changing their "
        "behavior is backward compatibility at the OS level - programs compiled "
        "against older kernels still work on newer ones."
    ),
    st=(
        "The most counterintuitive property of backward compatibility is "
        "that adding a new required field is always a breaking change - even "
        "if you provide a server-side default value. An existing consumer "
        "that sends a request without the new required field will receive a "
        "validation error if the server enforces the field as required. The "
        "only truly backward compatible way to add a field is to make it "
        "optional and handle its absence. This is why Protocol Buffers treats "
        "all fields as optional by default in proto3 - Google's internal "
        "experience showed that required fields were the most common source "
        "of backward compatibility failures."
    ),
    q1_hint=(
        "Think about the three cases: (1) changing `status` from string "
        "`'COMPLETED'` to integer `3` is a type change - always a breaking "
        "change. Consumers that deserialise the field as string will get a "
        "JSON parse error. (2) Adding a new status value `'PARTIALLY_REFUNDED'` "
        "is technically backward compatible at the type level but a breaking "
        "change at the application logic level for consumers with exhaustive "
        "switch/match statements that throw on unknown values. (3) Removing "
        "`'PENDING'` is a breaking change for any consumer that checks for "
        "`status=PENDING` in its business logic."
    ),
    q2_hint=(
        "Think about what the multi-currency Kafka migration means: you cannot "
        "change the existing `amount` field type. Add new fields: `currency` "
        "(default 'USD') and `currencyAwareAmount` (the full amount object). "
        "Transition: (1) publish events with both `amount` (backward compat) "
        "and the new fields; (2) existing consumers continue using `amount` "
        "(they ignore new fields); (3) consumers migrate to use `currency` + "
        "`currencyAwareAmount` and deploy; (4) after all consumers are "
        "migrated, stop publishing `amount` (after a defined sunset period). "
        "Schema Registry compatibility: BACKWARD_TRANSITIVE (new schema can "
        "read all old messages)."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your REST API has returned `timestamp` "
        "fields as Unix epoch milliseconds (e.g., `1699999999000`) for 3 "
        "years. A requirement to return ISO 8601 strings "
        "(`'2023-11-15T14:13:19Z'`) arrives. 50 consumers depend on the "
        "current epoch format. Design the migration without breaking consumers."
    ),
    q3_hint=(
        "Think about 'add a field, don't change an existing field': add a new "
        "field `timestampIso` (ISO 8601) alongside the existing `timestamp` "
        "(epoch milliseconds). Mark `timestamp` as deprecated in the OpenAPI "
        "spec (`deprecated: true`). After a 90-day migration window (with "
        "usage analytics showing which consumers still use `timestamp`), "
        "sunset `timestamp`. Explore whether content negotiation "
        "(`Accept-Datetime-Format: iso8601` header) can allow individual "
        "consumers to opt into the new format before the old format is "
        "removed, avoiding a hard migration deadline."
    ),
)

upgrade(
    "MSV-061 - Versioning Strategy.md",
    evo=(
        "API versioning became a necessary practice as REST APIs proliferated "
        "and backward compatibility guarantees proved insufficient for major "
        "changes. Fielding's original REST dissertation (2000) didn't prescribe "
        "versioning; early REST APIs had none. Stripe's API versioning strategy "
        "(2012) set a widely-copied standard: every API change is dated and "
        "versioned, clients pass the version they were built against, and the "
        "server supports all versions simultaneously. GraphQL (2015) proposed "
        "schema evolution (add, deprecate, never remove) as a versioning "
        "alternative. The discipline evolved from 'try not to break things' "
        "to 'explicit version management with defined sunset processes.'"
    ),
    tw_principle=(
        "An API version is a promise about interface stability. Versioning "
        "is not a technical decision; it is a business commitment about how "
        "long you will maintain backward compatibility for each version. "
        "The versioning strategy must answer: how long will v1 be supported? "
        "What triggers a major version? Who pays the cost of migration "
        "(consumer or provider)? These are business commitments, not "
        "engineering choices."
    ),
    tw_bullets=(
        "- **Operating system versions:** Windows, macOS, and Linux provide "
        "versioned API surfaces for user programs. Legacy support policies "
        "(Microsoft's 10 years for Windows 10) are versioning commitments.\n"
        "- **Browser compatibility:** Web APIs deprecate old features with "
        "versioned browser release timelines and compatibility tables - "
        "versioning strategy applied to browser APIs.\n"
        "- **Database drivers:** JDBC major versions represent interface "
        "contracts. Old drivers still work with new databases due to "
        "backward compatibility guarantees."
    ),
    st=(
        "URI versioning (the most popular REST versioning strategy) has a "
        "fundamental operational cost teams discover only at scale: when you "
        "have 5 API versions simultaneously (v1-v5), you effectively maintain "
        "5 separate services that all need security patches, infrastructure "
        "updates, and bug fixes. Netflix maintained 3-5 active API versions "
        "for years and documented this as their highest source of ongoing "
        "engineering maintenance cost. Stripe's approach (a single API version "
        "with dated client configurations) is more complex to implement but "
        "eliminates the multi-version maintenance burden entirely."
    ),
    q1_hint=(
        "Think about detecting which consumers still use `legacyId`: add a "
        "deprecation header (`Deprecation: true`, `Sunset: Sat, 01 Jan 2025 "
        "00:00:00 GMT`) to all responses that include `legacyId`, then monitor "
        "API gateway access logs for consumers still calling without a migration "
        "header. If a consumer processes the deprecation header correctly, they "
        "will log or alert. If consumers don't respond to the deprecation notice "
        "within 30 days of the sunset date, enforce the sunset by returning "
        "`null` for `legacyId` (one final warning) before removing the field "
        "entirely."
    ),
    q2_hint=(
        "Think about the arguments: URI versioning (visible in URL, easy to "
        "test with curl, no special header handling, easy to route in reverse "
        "proxies). Header versioning (cleaner URLs, decouples version from "
        "resource identity, but requires special client setup to test, and "
        "harder to cache correctly in CDNs). For a public REST API: URI "
        "versioning wins (external developers expect it, easy to discover "
        "and test). For internal gRPC: Protobuf field numbers handle backward "
        "compatibility natively, making URL versioning largely unnecessary "
        "- breaking changes are rare and coordinated internally."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your API is at v2 with 1000 active "
        "consumers. You need to release v3 with breaking changes. How do "
        "you release v3 without breaking v2 consumers, while creating "
        "incentive for consumers to migrate?"
    ),
    q3_hint=(
        "Think about what pressure without breaking means: announce v3 "
        "availability with a v2 sunset date (12-18 months out), provide "
        "migration guide and tooling, offer incentives for early migration "
        "(v3 features not available in v2, v3 higher rate limits, v2 rate "
        "limits gradually reduced). Add `Deprecation` and `Sunset` headers "
        "to v2 responses. Explore whether Stripe's approach (v2 consumers "
        "keep the same behavior forever until they explicitly upgrade, v3 "
        "is the default for new registrations) eliminates migration pressure "
        "but requires maintaining v2 indefinitely - what is the long-term "
        "business cost of that commitment?"
    ),
)

upgrade(
    "MSV-062 - Twelve-Factor App.md",
    evo=(
        "The Twelve-Factor App was published by Adam Wiggins (Heroku co-founder) "
        "in 2011 to document best practices for building SaaS applications, "
        "derived from Heroku's experience running thousands of apps. The twelve "
        "factors predated Kubernetes and Docker (containers later made several "
        "factors easier to implement). Kevin Hoffman's 'Beyond the Twelve "
        "Factor App' (2016) extended the methodology for microservices and "
        "cloud-native platforms. The discipline evolved from 'best practices "
        "for Heroku apps' to 'universal principles for cloud-native application "
        "design' built into Kubernetes, Cloud Foundry, and AWS Elastic Beanstalk."
    ),
    tw_principle=(
        "The twelve factors describe what 'cloud-native' means at the "
        "application level: the application explicitly declares its dependencies, "
        "reads configuration from the environment, writes to stdout rather than "
        "files, and can be started and stopped quickly. An application that "
        "violates these factors is hard to deploy, scale, and debug. An "
        "application that follows them is predictable, horizontally scalable, "
        "and operable by platform automation."
    ),
    tw_bullets=(
        "- **Docker containers:** A container that reads all configuration "
        "from environment variables and writes all output to stdout is a "
        "twelve-factor application by design - the container runtime enforces "
        "factors 3, 7, and 11.\n"
        "- **Kubernetes ConfigMaps and Secrets:** Implement Factor 3 (config "
        "in environment) for containerised applications without modifying the "
        "application code.\n"
        "- **Serverless functions:** AWS Lambda enforces several twelve-factor "
        "practices by design: fast startup/shutdown (Factor 9) and stateless "
        "processes (Factor 6)."
    ),
    st=(
        "The most counterintuitive twelve-factor finding is that Factor 9 "
        "(Disposability: fast startup and graceful shutdown) directly conflicts "
        "with the common practice of cache warm-up. Many applications claiming "
        "to be stateless actually load megabytes of data from a database at "
        "startup (violating Factor 9 while technically satisfying Factor 6). "
        "At scale, rolling restarts of 100 pods take 100 * startup_time rather "
        "than being instant. The solution is not to eliminate startup caches "
        "but to make them lazy-loaded (load on first request, not at startup) "
        "or use external caching (Redis) that is already warm when pods start."
    ),
    q1_hint=(
        "Think about each violation: (a) DB URL in committed properties file "
        "- violates Factor 3 (config in environment). Fix: move to Kubernetes "
        "Secret + environment variable. (b) User cart in HttpSession - violates "
        "Factor 6 (stateless processes). Fix: move cart to Redis so any pod "
        "can serve any user. (c) Writing to `/logs/app.log` - violates Factor "
        "11 (logs as event streams). Fix: write to stdout, let the platform "
        "aggregate. (d) H2 in tests, PostgreSQL in prod - violates Factor 10 "
        "(dev/prod parity). Fix: use PostgreSQL with Testcontainers in tests. "
        "(e) 4-minute startup - violates Factor 9 (disposability). Fix: lazy-"
        "load the cache on first request."
    ),
    q2_hint=(
        "Think about when dev/prod parity is acceptable to violate: (1) when "
        "the production dependency is expensive (Oracle DB) and a compatible "
        "open-source alternative (PostgreSQL) exists for testing; (2) when "
        "testing against the real dependency would cause external side effects "
        "(sending emails, charging payment cards); (3) when the test environment "
        "cannot access the production service (security, network). Risks of "
        "deviation: H2 does not support all PostgreSQL SQL syntax - queries "
        "that work on H2 may fail on PostgreSQL due to SQL dialect differences "
        "that are only discovered in production."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A legacy Java service violates multiple "
        "twelve-factor principles: stores state in JVM memory (sessions), "
        "reads config from a properties file on disk, and writes logs to a "
        "file. You need to containerize it on Kubernetes without rewriting "
        "the application. Design the migration that achieves twelve-factor "
        "compliance at the infrastructure level."
    ),
    q3_hint=(
        "Think about what can be fixed at the infrastructure level vs what "
        "requires code changes: logs to file (deploy a sidecar container that "
        "tails the log file and writes to stdout - no application code change); "
        "config from disk (mount a Kubernetes ConfigMap as a file at exactly "
        "the path the application reads from - no code change); in-memory "
        "session state (harder without code changes - evaluate whether sticky "
        "sessions via ingress annotation can serve as a temporary measure "
        "while the application is migrated to use Redis sessions). Identify "
        "which factors can be fixed with zero code changes vs which require "
        "application modifications."
    ),
)

upgrade(
    "MSV-063 - Sidecar Pattern (Microservices).md",
    evo=(
        "The Sidecar pattern emerged from the recognition that cross-cutting "
        "infrastructure concerns should not be implemented repeatedly in each "
        "service. Netflix's Prana sidecar (2012) externalised infrastructure "
        "logic from JVM services into a separate process. Lyft's Envoy (2016) "
        "generalised this to a standalone proxy. Istio (2017) made sidecar "
        "injection automated with a mutating webhook. CNCF's Dapr (2019) "
        "extended the sidecar model to include state management, messaging, "
        "and observability. The discipline evolved from 'embed infrastructure "
        "logic in each service' to 'delegate to a co-located infrastructure "
        "proxy that can be upgraded independently of the application.'"
    ),
    tw_principle=(
        "A sidecar separates infrastructure concerns from business logic, "
        "allowing both to evolve independently. Infrastructure changes (new "
        "retry policy, updated mTLS certificate, new tracing configuration) "
        "can be deployed to the sidecar without touching application code. "
        "Application business logic changes don't require infrastructure "
        "sidecar redeployment. This is the same separation of concerns as "
        "database drivers (infrastructure separate from SQL), OS kernels "
        "(infrastructure separate from user code)."
    ),
    tw_bullets=(
        "- **Log shippers (Filebeat):** A Filebeat agent running alongside "
        "an application and shipping its logs is a sidecar at the host level "
        "- log infrastructure separate from application logic.\n"
        "- **Database drivers:** A database driver is a sidecar at the library "
        "level - it handles connection management and protocol translation "
        "without requiring application code to know the wire protocol.\n"
        "- **Datadog agent:** The Datadog agent running as a sidecar container "
        "is infrastructure monitoring separate from application logic - the "
        "sidecar pattern for observability."
    ),
    st=(
        "The sidecar pattern's most counterintuitive failure mode is 'sidecar "
        "sprawl': when a service accumulates multiple sidecars for different "
        "concerns (observability, service mesh, secrets management, rate "
        "limiting), the sidecar infrastructure becomes more complex than the "
        "application itself. A Kubernetes pod with 5 containers (application "
        "+ 4 sidecars) has 5x the startup time, 5x the memory overhead, and "
        "5x the containers to monitor. The correct discipline is to consolidate "
        "infrastructure concerns into as few sidecars as possible (ideally one "
        "service mesh proxy like Envoy) rather than adding a sidecar per concern."
    ),
    q1_hint=(
        "Think about the trade-offs: library approach (each team adds OTel SDK "
        "per language, controls their own SDK version, must upgrade per-service); "
        "sidecar approach (platform team manages centrally, consistent across "
        "all languages, upgraded once for all services, but adds per-pod memory "
        "overhead and startup latency). For a polyglot team where consistency "
        "across Java/Python/Node.js/Go matters more than per-service control, "
        "the sidecar approach is correct. Switch to library approach if the "
        "team is homogenous (all Java) and wants fine-grained per-service "
        "instrumentation control."
    ),
    q2_hint=(
        "Think about where the added latency comes from: each sidecar-to-"
        "sidecar hop adds latency (TLS handshake + proxy processing). "
        "API Gateway → Order Service: 1 incoming sidecar hop. Order Service "
        "→ Payment Service: 1 outgoing + 1 incoming sidecar hop. Payment "
        "Service → Payment Provider: 1 outgoing sidecar hop. Total: ~4 hops. "
        "If the 50ms 'per hop' is the round-trip overhead, 4 hops = 200ms "
        "additional latency. Explore whether HTTP/2 connection reuse (Envoy "
        "maintains persistent upstream connections, amortising TLS handshake "
        "cost) reduces per-request overhead to sub-10ms per hop."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Istio releases a security patch requiring "
        "updating all 300 Envoy sidecars. Updating sidecars requires restarting "
        "all 300 pods, triggering rolling restarts of all applications. Design "
        "a process that minimises application disruption during sidecar "
        "security upgrades."
    ),
    q3_hint=(
        "Think about what minimises application disruption during sidecar "
        "upgrades: Pod Disruption Budgets (ensure no service drops below "
        "minimum availability during the rolling restart), rolling restart "
        "rate limits (restart pods in small batches across the cluster, "
        "not all services simultaneously), and Istio's Ambient Mesh (no "
        "per-pod sidecars, upgrades the per-node ztunnel DaemonSet without "
        "restarting application pods). Explore whether migrating to Ambient "
        "Mesh would eliminate this class of operational disruption entirely."
    ),
)

upgrade(
    "MSV-064 - Ambassador Pattern.md",
    evo=(
        "The Ambassador pattern was named by the Microsoft Azure Architecture "
        "Center in their 'Cloud Design Patterns' catalog (2015) as a pattern "
        "for offloading client connectivity tasks to a helper service. The "
        "pattern draws from the Sidecar pattern but specifically focuses on "
        "the client-side proxy role: the Ambassador handles retries, circuit "
        "breaking, authentication, and protocol translation on behalf of the "
        "main service. Netflix's Ribbon (2012) and Lyft's Envoy upstream "
        "cluster management are implementations. The discipline evolved from "
        "'implement client-side resilience in every service' to 'delegate "
        "to a dedicated Ambassador proxy.'"
    ),
    tw_principle=(
        "An Ambassador handles the complexity of talking to a specific external "
        "service, so the main application doesn't have to. The Ambassador knows "
        "how to handle retries, timeouts, authentication, and protocol "
        "translation for a specific downstream service. When the downstream "
        "service's interface changes, only the Ambassador needs to change. "
        "The same principle governs AWS SDKs (know how to talk to AWS), "
        "database drivers (know the database wire protocol), and OAuth "
        "client libraries (handle token refresh and redirect flows)."
    ),
    tw_bullets=(
        "- **AWS SDK:** The AWS SDK is an Ambassador for AWS services - handles "
        "request signing, retry logic, error handling, and protocol translation "
        "on behalf of your application code.\n"
        "- **Database driver:** A JDBC driver is an Ambassador for a specific "
        "database - handles the wire protocol, connection pooling, and query "
        "execution so application code only writes SQL.\n"
        "- **OAuth client library:** An OAuth library is an Ambassador for "
        "OAuth flows - handles token refresh, redirect flows, and token storage "
        "so application code only calls `getAccessToken()`."
    ),
    st=(
        "The Ambassador pattern has a subtle failure mode when combined with "
        "retry logic: the Ambassador can turn a momentary service degradation "
        "into a full outage through retry amplification. When a service "
        "degrades to 10% error rate, Ambassadors with 3 retries amplify load "
        "to 1.3x. When error rate rises to 50%, retries amplify load to 2.5x "
        "- more than doubling the load on an already struggling service. "
        "The amplification grows faster than the error rate, creating a "
        "feedback loop. The circuit breaker in the Ambassador is the "
        "essential companion to retry logic: it stops retrying once the "
        "error rate exceeds a threshold."
    ),
    q1_hint=(
        "Think about the load calculation: at 10% error rate, 20 req/s fail "
        "with 3 retries each. Ambassador load: 200 + (20 * 3) = 260 req/s "
        "(30% amplification). At 20% error rate: 200 + (40 * 3) = 320 req/s "
        "(60% amplification). At 50% error rate: 200 + (100 * 3) = 500 req/s "
        "(2.5x the original load). The amplification makes the failing service "
        "worse. Fix: a circuit breaker that opens when error rate exceeds 30% "
        "stops all retries (0 additional load) and lets the service recover "
        "without continued bombardment."
    ),
    q2_hint=(
        "Think about 3 arguments for explicit Ambassador over Istio: (1) "
        "lower operational overhead (no Istio control plane, no Envoy sidecar "
        "injection, fewer moving parts); (2) per-service customisation (each "
        "Ambassador tailored to its specific downstream without learning Istio "
        "VirtualService YAML); (3) no global blast radius (Istio control plane "
        "issues affect all services; Ambassador issues affect only one service). "
        "For a team of 8 engineers with 15 services: explicit Ambassador or "
        "Resilience4j library approach is likely more appropriate than "
        "Istio's operational overhead."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** The payment processor you proxy through "
        "an Ambassador switches to a webhook model (payment results sent "
        "asynchronously instead of synchronously). Existing callers expect "
        "synchronous responses. Design the Ambassador to support both the "
        "old synchronous callers and the new webhook model."
    ),
    q3_hint=(
        "Think about what the Ambassador must now do for synchronous callers: "
        "send the request to the processor, wait for the webhook (async), "
        "correlate the webhook to the original request by request ID, then "
        "return the result to the waiting caller. This is an Async-to-Sync "
        "adapter. Explore whether the Ambassador uses short-polling "
        "(periodically check for the webhook result) or long-polling "
        "(hold the connection open until the webhook arrives), what the timeout "
        "is for a webhook that never arrives, and whether the two models "
        "(sync and async) should be separate Ambassador endpoints or handled "
        "by a single routing implementation."
    ),
)

upgrade(
    "MSV-065 - Adapter Pattern (Microservices).md",
    evo=(
        "The Adapter pattern was formalised by the Gang of Four in 'Design "
        "Patterns' (1994). In microservices, it took on additional importance "
        "as teams integrated with legacy systems, third-party services, and "
        "services using different protocols (REST, SOAP, gRPC, GraphQL). "
        "The Anti-Corruption Layer (Eric Evans, 2003) is a DDD-specific "
        "application of the Adapter for domain model integrity. OpenAPI "
        "code generation (2015) made Adapter generation automated. The "
        "discipline evolved from 'hand-write translation code' to 'generate "
        "adapters from formal specifications with schema validation and "
        "type safety.'"
    ),
    tw_principle=(
        "An Adapter decouples the interface used by callers from the interface "
        "provided by a dependency. Callers use the Adapter's clean interface; "
        "the Adapter handles all translation and compatibility logic. When the "
        "dependency's interface changes (new API version, new field naming, "
        "protocol upgrade), only the Adapter changes. Callers are completely "
        "isolated from the change. The same principle governs database drivers "
        "(JDBC adapts SQL calls to database wire protocol), messaging clients "
        "(JMS adapts calls to broker protocol), and cloud SDKs."
    ),
    tw_bullets=(
        "- **JDBC database drivers:** JDBC translates standard SQL calls into "
        "database-specific wire protocol. Switching databases requires changing "
        "the driver (Adapter), not the application code.\n"
        "- **Message broker clients:** JMS Adapters translate JMS calls into "
        "broker-specific protocols (AMQP, STOMP). Switching brokers requires "
        "changing the JMS Adapter.\n"
        "- **OpenAPI code-generated clients:** An auto-generated REST client "
        "is an Adapter that translates method calls into HTTP requests. "
        "Regenerating the client updates the Adapter without touching "
        "application business logic."
    ),
    st=(
        "The Adapter pattern's most counterintuitive failure mode is 'adapter "
        "bloat': an Adapter that starts as a simple translation layer gradually "
        "accumulates business logic. Teams add retry (reasonable), then caching "
        "(reasonable), then business rule transforms (dangerous), then domain-"
        "specific error handling (the Adapter is now making business decisions). "
        "Six months later, the Adapter contains critical business logic that "
        "is not tested at the domain level, is not visible to domain experts, "
        "and is the first component to break when the external API changes. "
        "The discipline: Adapters translate data formats and protocols, "
        "never implement business rules."
    ),
    q1_hint=(
        "Think about what 'one Adapter with 4 version handlers' looks like: "
        "the Adapter exposes a single internal domain model interface to your "
        "service. Behind it, a version router selects the correct handler "
        "(V1Adapter, V2Adapter, V3Adapter, V4Adapter) based on the API version "
        "field. Fields in v4 but not v1: the internal model has these as "
        "optional/nullable, populated when v4 data is available, null for v1 "
        "responses. Error codes that changed meaning: a mapping table in each "
        "version handler translates version-specific error codes to canonical "
        "error codes in the internal model."
    ),
    q2_hint=(
        "Think about strategies to reduce legacy system load: (1) caching "
        "(cache responses for identical request parameters - reduces duplicate "
        "calls); (2) request coalescing (if multiple requests arrive with "
        "identical parameters in a short window, make one legacy call and "
        "return the result to all of them); (3) request queuing with rate "
        "limiting (queue requests, process at the legacy system's max rate "
        "of 3,000/s, queue the excess 2,000/s with higher latency); (4) "
        "circuit breaking (reject requests rather than amplifying load when "
        "the legacy system is overwhelmed). Best choice: caching + circuit "
        "breaking - lowest complexity, highest protection."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** The payment processor updates their API "
        "to require OAuth 2.0 authentication (replacing API key authentication). "
        "Your Adapter handles 1000 req/s to this processor. Design the "
        "authentication migration for the Adapter without causing downtime "
        "or requiring any consumer service code changes."
    ),
    q3_hint=(
        "Think about what the Adapter must now handle: OAuth token acquisition "
        "(client credentials flow), token caching (avoid OAuth server overload "
        "at 1000 req/s), token refresh before expiry, and retry with a fresh "
        "token on 401 responses. The migration sequence: (1) deploy Adapter "
        "with OAuth support (dual-mode: try OAuth first, fall back to API key); "
        "(2) verify OAuth works in production on the live traffic; (3) remove "
        "API key fallback from the Adapter. Zero consumer code changes required "
        "throughout - the authentication mechanism is entirely encapsulated "
        "within the Adapter."
    ),
)

print("\nBatch 6 (MSV-056 to MSV-065) complete.")
