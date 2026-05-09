#!/usr/bin/env python3
"""Upgrade MSV-036 through MSV-045 from v2.1 to v3.0."""
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
    "MSV-036 - Retry Strategy.md",
    evo=(
        "Retry strategies evolved from simple 'try again on failure' (1990s) "
        "to configurable policies with exponential backoff and jitter. The "
        "initial approach was synchronous retry: catch exception, wait, retry "
        "immediately. This caused retry storms: all callers retrying "
        "simultaneously overwhelmed the downstream service. 'Full Jitter' "
        "(Marc Brooker, AWS, 2015) added randomness to the backoff period, "
        "solving synchronized retry storms. gRPC's built-in retry policy (2019) "
        "standardised retry configuration at the protocol level. The discipline "
        "evolved from 'retry on any exception' to 'retry only idempotent "
        "operations, with jitter, within a deadline budget.'"
    ),
    tw_principle=(
        "Retries are not free. Each retry attempt adds latency, creates "
        "additional load on the downstream service, and can amplify a partial "
        "outage into a full one. The decision to retry must be based on three "
        "criteria: the idempotency of the operation (only retry idempotent "
        "operations), the retriability of the failure (network errors: "
        "retriable; business validation errors: not retriable), and the "
        "deadline budget (only retry if there is enough time for the retry "
        "to succeed within the caller's remaining deadline)."
    ),
    tw_bullets=(
        "- **Kafka producer retries:** A Kafka producer with `retries=5` and "
        "`retry.backoff.ms=100` applies retry strategy at the messaging layer "
        "- the same pattern as HTTP client retry, at a different protocol.\n"
        "- **Database connection retry:** A connection pool that retries "
        "connecting to a database when the connection is refused is applying "
        "retry strategy at the infrastructure level.\n"
        "- **DNS resolution retry:** A DNS client that retries resolution "
        "on SERVFAIL is applying retry strategy to infrastructure service "
        "discovery."
    ),
    st=(
        "The 'idempotency key' pattern for retry safety has a subtle failure "
        "mode: idempotency keys are only effective if the server stores them "
        "in the same transaction as the operation. If the server processes the "
        "payment and commits it, then tries to store the idempotency key and "
        "fails (network timeout before the key write is acknowledged), the next "
        "retry arrives with the same key, finds no record of it, and processes "
        "the payment again. The idempotency key must be committed atomically "
        "with the business operation in a single database transaction - not "
        "written after the operation completes."
    ),
    q1_hint=(
        "Think about the multiplication: A tries B up to 4 times (1 original "
        "+ 3 retries). Each B→C call can try C up to 4 times. Maximum B→C "
        "calls: 4 * 4 = 16. Worst-case latency: A's backoff ladder "
        "(100 + 200 + 400ms) plus B's backoff ladder for C (100 + 200 + 400ms). "
        "Deadline propagation solves this by passing the remaining deadline "
        "to B: if A's remaining deadline is 300ms, B can only attempt one C "
        "call (because 100ms backoff would exceed the 300ms budget), preventing "
        "the multiplication."
    ),
    q2_hint=(
        "Think about what '0.3% duplicate charges' means in the idempotency "
        "key flow: the server committed the charge AND wrote the idempotency "
        "key. But the network dropped the response. Correct idempotency key "
        "implementation: store the idempotency key in the SAME transaction "
        "as the charge record. The bug is storing the key after the transaction "
        "commits (two separate writes). Fix: write both the charge record and "
        "the idempotency key in a single atomic transaction so that either "
        "both are committed or neither is."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your payment service accepts `POST /charge` "
        "with an idempotency key. It calls an external payment processor that "
        "does not support idempotency keys. Design the complete system so that "
        "`POST /charge` is safe to retry end-to-end, even though the external "
        "processor is not idempotent."
    ),
    q3_hint=(
        "Think about where idempotency can be enforced before calling the "
        "external processor: check if this idempotency key already has a "
        "committed result in your local database before calling the external "
        "API. If a result exists, return it directly. If not, call the external "
        "API and store the result atomically with the idempotency key. Explore "
        "whether the Outbox pattern (write payment command to outbox table in "
        "same transaction as idempotency key check, a background relay calls "
        "the external API exactly once) provides stronger exactly-once guarantees "
        "than an inline synchronous approach."
    ),
)

upgrade(
    "MSV-037 - Fallback Strategy.md",
    evo=(
        "The Fallback pattern was popularised by Netflix Hystrix (2012) as the "
        "companion to circuit breaking: when the circuit opens, what should "
        "happen instead of a 500 error? Netflix classified fallback responses "
        "as Static (hardcoded default), Cached (last-known-good response), "
        "Degraded (simpler computation without the failed dependency), and Fail-"
        "silent (return null, handled by caller). The discipline evolved from "
        "'catch exception, throw default response' to 'design fallback for each "
        "dependency as part of system design upfront - before failures occur.'"
    ),
    tw_principle=(
        "Every external dependency has a fallback strategy, even if the "
        "fallback is 'fail gracefully with a clear error message.' The fallback "
        "is the planned behavior when a dependency is unavailable - not a "
        "safety net for exceptional cases. A system that has designed fallbacks "
        "for all dependencies has designed for failure, which is the correct "
        "resilience design posture."
    ),
    tw_bullets=(
        "- **Cache with database fallback:** Cache hit returns cached value; "
        "cache miss falls back to the database. The cache is the primary source; "
        "the database is the fallback. Same fallback pattern.\n"
        "- **CDN with origin fallback:** CDN hit returns cached content; "
        "cache miss falls back to origin server. Same pattern applied to "
        "content delivery.\n"
        "- **Read replica with primary fallback:** Read replica serves reads; "
        "if unavailable, falls back to the primary. Same fallback pattern "
        "applied to database replication."
    ),
    st=(
        "The most dangerous fallback is one that returns stale data without "
        "signaling that the data is stale. A product page showing a cached "
        "price from 4 hours ago with no indication it may have changed actively "
        "misleads users - and can cause business losses (oversold products, "
        "incorrect prices). A stale data fallback should show the data with a "
        "visual or semantic indicator that it may not be current, and should "
        "limit the stale TTL to a business-acceptable window. A fallback that "
        "silently returns arbitrarily old data is worse than a clear, honest "
        "error message."
    ),
    q1_hint=(
        "Think about what 'stale inventory data' means for different types of "
        "decisions: showing 'in stock' when actually out of stock causes "
        "overselling (high business cost, requires compensation); showing 'out "
        "of stock' when actually in stock causes lost sales (recoverable). The "
        "fallback design must ask: what is the business cost of each type of "
        "stale data error? If overselling risk is high, the stale inventory "
        "fallback should show 'check availability' rather than a specific stock "
        "level that may be incorrect."
    ),
    q2_hint=(
        "Think about what happens at the 1-hour mark vs 5-hour mark with a "
        "30-second TTL: the cache refreshes every 30 seconds from the live "
        "service. If the service goes down, the last cached value becomes stale "
        "after 30 seconds. At 1 hour: cache is 1 hour stale. At 5 hours: cache "
        "is 5 hours stale. Explore whether a two-TTL design (short TTL=30s for "
        "live-service freshness, long TTL=2h for fallback labeled as stale) "
        "combined with a circuit breaker that opens after N failures and returns "
        "the long-TTL cached value provides the specified 2-hour graceful "
        "degradation window before transitioning to a clear error state."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your system has a fallback chain: live "
        "service → short-TTL cache → long-TTL cache → static default. In "
        "production you discover the static default (set 2 years ago) contains "
        "incorrect data and cannot be updated without a code deployment. "
        "Redesign the fallback chain so static defaults can be updated without "
        "a code deployment."
    ),
    q3_hint=(
        "Think about where static defaults could be stored instead of hardcoded "
        "in source code: a configuration service (LaunchDarkly, AWS AppConfig), "
        "a long-TTL cache pre-populated with authoritative defaults, or a "
        "static JSON file in S3 read at startup with a local copy cached. "
        "Explore whether 'defaults as configuration' (stored in a system that "
        "can be updated without deployment, cached locally so the fallback "
        "works even if the config service is unavailable) provides both "
        "operational flexibility and high availability."
    ),
)

upgrade(
    "MSV-038 - Saga Pattern (Microservices).md",
    evo=(
        "The Saga pattern was introduced by Garcia-Molina and Salem in their "
        "1987 database paper 'Sagas' as a long-running transaction decomposition "
        "technique. The pattern was rediscovered by the microservices community "
        "(2015-2018) when distributed transactions proved incompatible with "
        "service independence. Chris Richardson's 'Microservices Patterns' "
        "(2018) established Saga as the standard distributed consistency "
        "pattern, distinguishing Choreography Sagas (event-driven, decentralised "
        "coordination) from Orchestration Sagas (centralised coordinator). "
        "The discipline evolved from 'use distributed transactions' to "
        "'design explicit compensating transactions for every saga step.'"
    ),
    tw_principle=(
        "A Saga is a sequence of local transactions, each with a compensating "
        "transaction. Designing the compensation upfront forces you to reason "
        "about failure at every step. This is the correct design posture for "
        "distributed systems: design for failure paths as explicitly as for "
        "success paths. Any long-running workflow spanning multiple systems "
        "should have explicit compensation logic designed before the first "
        "line of success-path code is written."
    ),
    tw_bullets=(
        "- **Flight booking:** Reserve seat A, reserve seat B, charge card. "
        "If card fails, release both seats. The compensation is explicitly "
        "designed into the workflow before any code is written.\n"
        "- **Kubernetes pod scheduling:** Kubernetes admits a pod, schedules "
        "it, starts containers, and cleans up on failure - a platform-level "
        "saga where each step has a corresponding cleanup action.\n"
        "- **Hotel + car rental bundle:** Book hotel, book rental, charge "
        "card. If the car is unavailable, cancel the hotel. Compensation "
        "logic is the business requirement, not an afterthought."
    ),
    st=(
        "The most counterintuitive property of sagas is that compensating "
        "transactions are not true rollbacks. A compensation executes a new "
        "operation that undoes the business effect of a previous step - but "
        "it cannot undo the fact that the step occurred. If a "
        "'SendConfirmationEmail' step runs and the user receives the email "
        "before the saga fails, the compensation 'SendCancellationEmail' "
        "cannot un-send the original. The customer received both. Saga "
        "compensations are semantic undos, not transactional undos. Systems "
        "that treat compensation as equivalent to a database rollback design "
        "compensation logic that is provably incorrect."
    ),
    q1_hint=(
        "Think about what a 'failed compensation step' means for the saga: "
        "it cannot proceed forward (step 4 failed) and cannot proceed backward "
        "(step 3 compensation failed). The saga is stuck in an inconsistent "
        "intermediate state. Explore whether the correct design is to retry "
        "the failed compensation step (if the compensation is idempotent and "
        "the failure is transient) or to route the saga to a 'compensation "
        "failed' state and place it in a dead-letter queue for manual "
        "resolution, with the order labeled 'pending resolution' in the UI."
    ),
    q2_hint=(
        "Think about what adding a loyalty step means in each model: "
        "choreography (Payment Service must now subscribe to "
        "LoyaltyPointsPending instead of InventoryReserved - it must change; "
        "Loyalty Service must publish LoyaltyPointsPending after consuming "
        "InventoryReserved - it must change; Order Service must change event "
        "flow; potentially 3-4 services change). Orchestration: only the "
        "Orchestrator (Order Saga) adds the new Loyalty step - 1 service "
        "changes. This is the fundamental choreography trade-off at scale."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your Orchestration Saga persists saga "
        "state in a PostgreSQL table. At 10,000 checkouts/second, the saga "
        "state table is a write bottleneck. Design a saga state persistence "
        "strategy that handles 10,000 sagas/second without the bottleneck."
    ),
    q3_hint=(
        "Think about what saga state persistence needs: durability (saga "
        "survives orchestrator crashes), low write latency (on the hot checkout "
        "path), and replay capability (audit, incident investigation). Explore "
        "whether an append-only event store (Kafka: each saga step transition "
        "is an event, saga state is reconstructed from events on recovery) "
        "replaces the write-heavy state table with a write-optimised log, and "
        "whether the orchestrator can hold in-memory state for active sagas "
        "while Kafka provides the durable backup."
    ),
)

upgrade(
    "MSV-039 - Distributed Transaction.md",
    evo=(
        "Two-Phase Commit (2PC) was proposed by Jim Gray in 1978 as the "
        "solution for atomicity across multiple nodes. XA transactions "
        "(X/Open DTP, 1991) standardised 2PC for distributed databases. "
        "The Paxos consensus algorithm (Leslie Lamport, 1989) provided a "
        "foundation for agreement without a single coordinator. In "
        "microservices, teams discovered that 2PC's requirements (all "
        "participants locked during commit, coordinator as single point of "
        "failure) were incompatible with service independence requirements. "
        "Saga became the preferred alternative. The discipline evolved "
        "from 'use 2PC for cross-service consistency' to 'design for "
        "eventual consistency with explicit compensation.'"
    ),
    tw_principle=(
        "Distributed consistency and high availability are in direct "
        "tension. 2PC requires all participants to be available and "
        "responsive for the full duration of the transaction - a 100ms "
        "transaction has a 100ms window where all participants must be "
        "locked and available. Every distributed transaction is a bet that "
        "availability will hold for its duration. When that bet fails, "
        "the transaction blocks until the coordinator recovers."
    ),
    tw_bullets=(
        "- **Consensus protocols:** Raft and Paxos solve distributed "
        "agreement using quorum-based consensus rather than all-or-nothing "
        "2PC commit - achieving consistency without a single coordinator "
        "blocking on all participants.\n"
        "- **Synchronous database replication:** All replicas must "
        "acknowledge before commit - strong consistency at the cost of "
        "availability if any replica is slow or unreachable.\n"
        "- **Git push:** Local commit (local consistency) then push to "
        "remote (remote consistency eventually) - eventual consistency "
        "applied to distributed version control."
    ),
    st=(
        "The most dangerous property of 2PC is the blocking period when "
        "the coordinator crashes after receiving all YES votes but before "
        "sending COMMIT. All participants are in 'prepared' state: resources "
        "locked, cannot proceed or abort unilaterally. If the coordinator's "
        "transaction log is unavailable, participants remain blocked until "
        "the coordinator recovers - which can take minutes to hours in a "
        "real production failure. Teams using 2PC in microservices often "
        "discover this blocking behavior for the first time during their "
        "first coordinator-host failure in production."
    ),
    q1_hint=(
        "Think about what 'prepared' state means: both participants have "
        "locked resources and are waiting for a decision. The new coordinator "
        "reads the WAL, sees all-YES was received, and by protocol must send "
        "COMMIT (aborting would violate the atomicity guarantee since both "
        "participants agreed). It sends COMMIT and both proceed normally. "
        "Now consider corrupt WAL: no coordinator has the transaction state. "
        "Both participants are stuck indefinitely - this is the 'blocking "
        "problem' of 2PC and requires DBA manual intervention to resolve."
    ),
    q2_hint=(
        "Think about what XA fails at in microservices: XA holds locks on "
        "all participants from PREPARE to COMMIT. If any participant restarts "
        "during this window, XA enters a blocking state. With saga: each step "
        "completes and releases locks immediately; compensation handles "
        "failures. The saga's cost vs XA: saga cannot provide true atomicity "
        "(intermediate state is visible during execution); XA provides apparent "
        "atomicity (no intermediate state visible externally) at the cost of "
        "availability during the transaction window."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A financial system requires that account "
        "debit and account credit be atomic - either both happen or neither. "
        "The two accounts live in different microservices. Design the strongest "
        "possible consistency guarantee without using 2PC, and specify what "
        "consistency level this achieves."
    ),
    q3_hint=(
        "Think about what 'strongest without 2PC' means: the Outbox pattern "
        "(debit + debit-event in one local transaction; event consumer applies "
        "credit idempotently) provides eventual consistency with at-least-once "
        "delivery and no data loss. The window of inconsistency is bounded to "
        "the event processing latency (typically milliseconds to seconds). "
        "Explore whether the business requirement actually needs true atomicity "
        "or whether a bounded-eventual model (both operations complete within "
        "N seconds or the transaction is flagged for manual review) satisfies "
        "the regulatory requirement."
    ),
)

upgrade(
    "MSV-040 - Event-Driven Microservices.md",
    evo=(
        "Event-driven microservices emerged from combining event-driven "
        "architecture (EDA, 1990s) with the microservices model (2012-2015). "
        "Early microservices favoured REST APIs for simplicity, but at scale, "
        "synchronous REST coupling caused cascading failures and latency chains. "
        "The Confluent Platform (2014) and managed Kafka made event-driven "
        "architectures operationally accessible. Martin Fowler's 'Event-Driven "
        "Architecture' and Chris Richardson's patterns systematised async "
        "communication. The discipline evolved from 'services calling services' "
        "to 'services emitting events, services reacting to events' - with the "
        "event log as the source of coordination truth."
    ),
    tw_principle=(
        "Events are facts, not commands. An event says 'this happened' "
        "(OrderPlaced, PaymentProcessed). A command says 'do this' (PlaceOrder, "
        "ProcessPayment). Events are immutable records of things that occurred; "
        "commands are instructions that may or may not be executed. Event-driven "
        "systems are more loosely coupled because producers don't know or care "
        "who consumes their events - the event is published regardless."
    ),
    tw_bullets=(
        "- **Database WAL / CDC:** PostgreSQL's Write-Ahead Log is an event "
        "log of all database changes. CDC reads this log and publishes events "
        "to other systems - event-driven architecture applied to database "
        "replication.\n"
        "- **Git commits:** A git commit log is an event log of code changes. "
        "The distributed model works because each commit is an immutable fact "
        "that any client can consume.\n"
        "- **Audit logs:** An immutable audit log is an event log of system "
        "actions. The audit log is useful precisely because events are facts "
        "that cannot be changed or deleted after the fact."
    ),
    st=(
        "The most counterintuitive finding about event-driven microservices "
        "is that they are harder to debug than synchronous microservices, not "
        "easier. In a synchronous system, tracing a failure means following a "
        "single request trace through a linear call chain. In an event-driven "
        "system, one user action can trigger 20 events across 10 services, "
        "each with its own retry logic, consumer group, and processing order. "
        "An incident requires correlating events across multiple Kafka topics "
        "and service logs with no single trace ID linking them. Event-driven "
        "architecture requires investment in distributed tracing (correlation "
        "IDs in event headers, Jaeger/Zipkin) to be debuggable in production."
    ),
    q1_hint=(
        "Think about what safe schema evolution requires: new consumers must "
        "read old events (forward compatibility) and existing consumers must "
        "read new events (backward compatibility). Adding an optional field "
        "with a default value is backward compatible for existing consumers "
        "that ignore it. Deployment order: (1) add the field to producers "
        "and publish with it, (2) deploy consumers that use the new field "
        "with fallback to default for old events that lack it, (3) set schema "
        "registry to BACKWARD compatibility. Never add a required field to "
        "an existing event schema."
    ),
    q2_hint=(
        "Think about what '200ms lag' means for the user immediately checking "
        "loyalty points after checkout: the points update is in flight, not "
        "yet applied. The correct UX is to show 'Points will be credited "
        "shortly' immediately after checkout - an explicit acknowledgment of "
        "async processing. Explore whether an 'optimistic update' in the UI "
        "(show the expected points increment immediately based on the order "
        "total, reconcile with server on next page load) provides the right "
        "user experience without requiring synchronous backend coordination."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** After 6 months, 15 consumers are reading "
        "the same 3 events but doing slightly different things with them. A "
        "colleague proposes centralising the common event processing into a "
        "shared consumer service. Evaluate this proposal."
    ),
    q3_hint=(
        "Think about what a 'shared consumer service' means for loose coupling: "
        "you are reintroducing the same coupling that event-driven architecture "
        "was designed to eliminate. The shared consumer becomes a single point "
        "of change for 15 different business processes. Explore whether the "
        "actual duplication (schema parsing, authentication, common data "
        "transformations) can be extracted into a shared library without "
        "coupling the business logic, so 15 consumers can deploy independently "
        "while sharing only infrastructure concerns."
    ),
)

upgrade(
    "MSV-041 - Eventual Consistency (Microservices).md",
    evo=(
        "Eventual consistency was formalised by Werner Vogels (Amazon CTO) in "
        "his 2008 paper 'Eventually Consistent.' The CAP theorem (Eric Brewer, "
        "2000) established the theoretical foundation: during a network "
        "partition, a system must choose between consistency and availability. "
        "Amazon's choice of AP (availability over consistency) led to "
        "DynamoDB's eventual consistency model (2007). The microservices "
        "community adopted eventual consistency as the default for inter-"
        "service communication, with strong consistency reserved for single-"
        "service boundaries. The discipline evolved from 'all data should be "
        "strongly consistent' to 'choose the right consistency model per data "
        "type based on business requirements.'"
    ),
    tw_principle=(
        "Most data in most systems does not require strong consistency. The "
        "key question is not 'how do we make everything strongly consistent?' "
        "but 'which data requires strong consistency, and what is the cost of "
        "temporary inconsistency for the rest?' Strong consistency costs "
        "availability and latency; eventual consistency costs reasoning "
        "complexity. Identifying which data falls into which category is the "
        "fundamental consistency design decision."
    ),
    tw_bullets=(
        "- **DNS:** DNS is an eventually consistent distributed database. An "
        "A record change propagates globally over minutes to hours - acceptable "
        "because the old IP usually still works during propagation.\n"
        "- **E-commerce search:** Product search results that don't reflect "
        "the last 5 minutes of inventory changes are eventually consistent. "
        "The inconsistency window is acceptable because search is a convenience "
        "feature.\n"
        "- **Social media counters:** A like count that shows a slightly stale "
        "number is eventually consistent. The business value of exact consistency "
        "is low; the availability cost of strong consistency is high."
    ),
    st=(
        "The most counterintuitive finding about eventual consistency is that "
        "it is not weaker than strong consistency in all use cases - it is "
        "stronger in availability. A strongly consistent system that refuses "
        "to serve reads during a network partition (to avoid stale data) "
        "provides zero availability during the partition. An eventually "
        "consistent system that serves reads during the partition (accepting "
        "potential staleness) provides continued service. For systems where "
        "'some information is better than no information,' eventual consistency "
        "is the correct choice. Consistency is a spectrum, not a binary."
    ),
    q1_hint=(
        "Think about what 'two users reading 1 in stock' means for saga design: "
        "both sagas place orders successfully (order created), both try to "
        "reserve inventory. The inventory service uses optimistic locking: "
        "one succeeds (stock becomes 0), the other fails with a conflict. "
        "The failing saga runs compensation (cancel order). Explore whether "
        "making the inventory reservation step strongly consistent (optimistic "
        "locking in the Inventory Service's own database) while keeping the "
        "rest of the system eventually consistent is the correct granularity "
        "- strong consistency only where the invariant must be enforced."
    ),
    q2_hint=(
        "Think about what the specific inconsistency is: the password reset "
        "service uses the Notification Service's cached email (stale) instead "
        "of the User Service's current email (fresh). The fix: the password "
        "reset service should call the User Service API directly to get the "
        "current email, not rely on the Notification Service's cached copy. "
        "Explore whether 'read your own writes' (the User Service guarantees "
        "that reads after a write see the new value) applied to the User "
        "Service API provides the specific consistency guarantee without making "
        "the entire email update path synchronous."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A new regulatory requirement states that "
        "account balances shown in monthly statements must exactly match the "
        "balances in the transaction service at the end of the month. Your "
        "system uses eventual consistency between the Transaction Service and "
        "the Statement Service. Design the consistency strategy for monthly "
        "statement generation."
    ),
    q3_hint=(
        "Think about what 'consistent at report generation time' means: a "
        "point-in-time snapshot guaranteed to be consistent at midnight on "
        "the last day of the month. Explore whether event sourcing (reconstruct "
        "account balance from all events up to end-of-month timestamp) provides "
        "point-in-time consistency for regulatory reports, and whether a "
        "dedicated 'reporting snapshot' process (triggered at month-end, reads "
        "directly from the Transaction Service's write store, stores an "
        "immutable snapshot) provides the regulatory guarantee without making "
        "the real-time system strongly consistent."
    ),
)

upgrade(
    "MSV-042 - Data Isolation per Service.md",
    evo=(
        "Data isolation per service emerged as the defining constraint of "
        "microservices architecture. Fowler and Lewis (2014) stated that "
        "microservices 'manage their own data.' This was a direct reaction "
        "against SOA's 'integration database' pattern where multiple services "
        "shared tables and foreign keys. Teams found that shared databases "
        "created the strongest possible coupling: a schema change in one "
        "service broke other services without any API change. Sam Newman's "
        "'Building Microservices' (2015) established 'Database per Service' "
        "as a core principle. The discipline evolved from 'one big shared "
        "database' to 'each service owns its data and exposes it only "
        "through its API.'"
    ),
    tw_principle=(
        "Data ownership is the foundation of service independence. A service "
        "that can have its database schema changed by another service is not "
        "independent - it is coupled at the deepest level. Data isolation is "
        "not just a technical choice; it is the operational practice that "
        "enables independent deployment, independent scaling, and independent "
        "failure domains. The service boundary and the data ownership boundary "
        "must coincide."
    ),
    tw_bullets=(
        "- **DDD aggregates:** Each aggregate owns its data and shares no "
        "tables with other aggregates - data isolation at the domain model "
        "level, before it reaches the infrastructure layer.\n"
        "- **File system permissions:** Each process owns specific files with "
        "specific read/write permissions - data isolation at the OS level.\n"
        "- **Kubernetes namespaces:** Each namespace owns specific resources "
        "with network policies restricting cross-namespace access - data "
        "isolation at the cluster level."
    ),
    st=(
        "The most counterintuitive finding about data isolation is that it "
        "creates 'JOIN poverty.' When all data was in one database, a complex "
        "report required one SQL query. With data per service, the same report "
        "requires fetching data from 5 services and joining it in application "
        "code - slower, more complex, and more fragile than a SQL join. Teams "
        "that adopt data isolation without planning for reporting workloads "
        "discover this when the first quarterly report takes 10 minutes instead "
        "of 5 seconds. The solution is dedicated reporting infrastructure "
        "(data warehouse, denormalised read stores, event-driven projections) "
        "that provides reporting capability without shared database coupling."
    ),
    q1_hint=(
        "Think about what 'referential integrity without foreign keys' means: "
        "at order creation time, the Order Service calls the Inventory Service "
        "API to validate the product exists and has sufficient stock. This is "
        "an optimistic check: the product could be deleted between the check "
        "and the saga's inventory reservation step. The saga's reservation "
        "step (which calls the Inventory Service transactionally) is the "
        "correct place to enforce the strongly consistent 'sufficient stock' "
        "invariant. Explore what the Order Service should do if the Inventory "
        "Service is down during order creation (accept with a pending status, "
        "retry the check, or reject)."
    ),
    q2_hint=(
        "Think about the three report approaches: (1) API join (call both "
        "services' APIs, join in memory - real-time, but N+1 API calls at "
        "scale, high latency); (2) event-driven read store (subscribe to "
        "events from both services, build denormalised reporting table - "
        "near-real-time, low query latency, complex to maintain); (3) ETL "
        "data warehouse (periodic extract from each DB, load into warehouse, "
        "SQL reports - simple queries, consistent at ETL time, inherently "
        "delayed). Weekly batch report: data warehouse is the right choice. "
        "Real-time dashboard: event-driven read store."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Three teams use separate schemas in a "
        "single PostgreSQL instance and claim 'data isolation.' They now want "
        "to introduce Kafka for async communication. Should they migrate to "
        "separate database instances before or after introducing Kafka? "
        "What are the risks in each order?"
    ),
    q3_hint=(
        "Think about what Kafka changes: async communication via Kafka reduces "
        "the need for synchronous cross-service SQL reads (a major reason to "
        "separate databases). Introducing Kafka first establishes async "
        "communication patterns that make the subsequent database split easier "
        "(fewer synchronous dependencies to migrate). Separating databases "
        "first without async communication increases the risk that teams "
        "work around the isolation by adding more cross-service API calls. "
        "Explore the order that minimises the risk of re-introducing coupling "
        "during the migration."
    ),
)

upgrade(
    "MSV-043 - CQRS in Microservices.md",
    evo=(
        "CQRS was coined by Greg Young (2010), building on Bertrand Meyer's "
        "CQS principle (1988). CQS separated methods into commands (change "
        "state) or queries (return state). CQRS elevated this to an "
        "architectural pattern: separate write and read data models. Event "
        "sourcing naturally pairs with CQRS (write model = event store, read "
        "model = projection). Martin Fowler's 'CQRS' article (2011) popularised "
        "it in the microservices context. The discipline evolved from CQS at "
        "the method level to full architectural separation with different data "
        "stores, allowing each to be optimised independently for its workload."
    ),
    tw_principle=(
        "Read and write workloads have fundamentally different requirements. "
        "Writes need transactional consistency and audit trails. Reads need "
        "low latency, flexible querying, and denormalised data for fast "
        "assembly. Forcing both to use the same data model means the model "
        "is suboptimal for both. CQRS is the recognition that "
        "'one data model for all uses' is the wrong constraint for systems "
        "with distinct read and write characteristics."
    ),
    tw_bullets=(
        "- **Database read replicas:** Write to primary (write model), read "
        "from replicas (read model), with replication as the projection "
        "mechanism - CQRS at the database infrastructure level.\n"
        "- **Search indexes (Elasticsearch):** Write to PostgreSQL (write "
        "model), query Elasticsearch (read model) - CQRS with a specialised "
        "read store for full-text search.\n"
        "- **CDN caching:** Origin server is the write model; CDN edges are "
        "the read model. Cache invalidation is the projection mechanism - "
        "CQRS applied to content delivery."
    ),
    st=(
        "CQRS's most dangerous failure mode is projection divergence: when "
        "the read model falls out of sync with the write model. This happens "
        "due to projection builder bugs, event schema changes processed "
        "incorrectly, or consumer lag. Once a projection is wrong, the fix "
        "is a full rebuild - which for a large event store can take hours. "
        "During rebuild, either the read model is stale (serve old data) or "
        "unavailable (serve errors). The mitigation is a versioned projection "
        "builder that can run in parallel with the current projection, be "
        "verified against known-good test cases, and cut over atomically "
        "when verified."
    ),
    q1_hint=(
        "Think about what 'backfill without direct write store access' means: "
        "the projection builder cannot JOIN against the PostgreSQL write store. "
        "Explore whether publishing a new event type `DiscountDataBackfilled` "
        "(a one-time migration script reads `discount_percentage` from the "
        "write store, publishes one event per affected order to the event log) "
        "allows the projection builder to process these backfill events and "
        "update `order_views` through its normal event consumption path, "
        "without ever directly querying the write store from the projection."
    ),
    q2_hint=(
        "Think about what zero-downtime rebuild means sequentially: (1) create "
        "`order_views_v2` table; (2) start new projection builder consuming "
        "from event log start into `order_views_v2`; (3) while catching up, "
        "new orders still write to `order_views` (the current read model); "
        "(4) when `order_views_v2` catches up to present, atomically redirect "
        "read queries from `order_views` to `order_views_v2` (application "
        "config change); (5) drop `order_views`. The critical step: the "
        "cut-over must be atomic and the two read models must be identical "
        "at cut-over time."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your CQRS read model is built from 3 "
        "million events. Rebuilding it takes 45 minutes. During a production "
        "incident, the read model is found to be corrupt. Design the zero-"
        "downtime read model recovery strategy that serves reads during the "
        "45-minute rebuild."
    ),
    q3_hint=(
        "Think about what options exist for serving reads during rebuild: "
        "(a) serve stale reads from the corrupt model (known-wrong data for "
        "45 minutes), (b) route reads to the write store (strong consistency, "
        "but write store load spike), (c) maintain a previous version of the "
        "read model as a versioned fallback until the new version is verified. "
        "Explore whether a 'two-version deployment' strategy (always keep "
        "the previous read model until the new one is verified) provides the "
        "recovery capability and what the storage overhead of versioned read "
        "models is."
    ),
)

upgrade(
    "MSV-044 - Event Sourcing in Microservices.md",
    evo=(
        "Event sourcing appeared in Domain-Driven Design contexts (Greg Young, "
        "Eric Evans, 2005-2010) as a way to represent aggregate state as a "
        "sequence of events rather than a mutable record. Greg Young's "
        "influential talks (2010-2012) formalised the pattern. EventStoreDB "
        "(Greg Young, 2012) provided the first purpose-built event store "
        "database. Axon Framework (2009) and Axon Server (2018) provided "
        "Java-native event sourcing infrastructure. The discipline evolved "
        "from 'store current state' to 'store the immutable history of "
        "changes, derive current state from history' - making the history "
        "of changes a first-class citizen."
    ),
    tw_principle=(
        "The current state of any system is the aggregate of all events that "
        "have happened to it. This is not a database pattern - it is how the "
        "real world works. Bank accounts don't store balances; they store "
        "transactions and compute the balance. Git doesn't store the current "
        "file state; it stores diffs and computes the current state. Event "
        "sourcing makes this pattern explicit in the software model, providing "
        "a complete audit trail and enabling temporal queries as a natural "
        "consequence."
    ),
    tw_bullets=(
        "- **Database WAL:** PostgreSQL's Write-Ahead Log is event sourcing "
        "at the database engine level - all changes recorded as events, "
        "current state derived by replaying them.\n"
        "- **Git version control:** Every commit is an event; current code "
        "state is derived by replaying commits from the initial commit. "
        "Git branches and time-travel are the same as event sourcing "
        "projections and temporal queries.\n"
        "- **Kafka as source of truth:** Using Kafka topics as the system "
        "of record (not just messaging) is event sourcing at the platform "
        "level - events are permanent, services derive their state from the "
        "event log."
    ),
    st=(
        "Event sourcing's most counterintuitive property is that it does not "
        "eliminate schema migration - it makes schema migration permanent and "
        "irreversible. In a traditional database, ALTER TABLE transforms all "
        "rows to the new format once. In an event store, old events remain "
        "in the old format forever (you cannot change immutable history). "
        "Every code change touching an event schema must include an upcaster "
        "(a function that transforms old event format to new format on read). "
        "Over time, a system accumulates dozens of upcasters. After 5 years, "
        "loading an aggregate may require running 15 upcasters sequentially. "
        "This 'upcaster debt' accumulates and teams rarely plan for it."
    ),
    q1_hint=(
        "Think about what the race condition is: read snapshot at sequence "
        "49,990, then read events 49,991 to present. Between these two reads, "
        "event 49,991 is appended. You read it correctly. The real concern is "
        "whether the aggregate loaded from events through 50,000 is processed "
        "with command validation against the correct version. Explore whether "
        "optimistic concurrency control (check that the version you built "
        "state from matches the current version before processing a command) "
        "solves the race condition, and whether eventual consistency during "
        "read (load + serve) is acceptable here."
    ),
    q2_hint=(
        "Think about what 'upcasting' means: a function registered in the "
        "event deserialization pipeline that transforms an old event format "
        "to the current format on read. Old events remain unchanged in the "
        "store (immutable). When new code reads an old event, the upcaster "
        "transforms it transparently. The upcaster must handle: old event "
        "without `discountPercentage` (default to 0 or null), and new event "
        "with `discountPercentage` (pass through unchanged). Explore whether "
        "the upcaster should be a read-time transformation (event store "
        "approach) or a one-time migration script (simpler but loses "
        "immutability property)."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** After 2 years, your order aggregate has "
        "20 event types, 8 upcasters, and average aggregate load time has "
        "grown from 50ms to 400ms. The team debates: add more snapshots "
        "(performance fix) vs migrate to a traditional database (architectural "
        "change). What criteria determine the right choice?"
    ),
    q3_hint=(
        "Think about what the 400ms load time means for your specific usage: "
        "is the Order aggregate loaded on every checkout (hot path) or only "
        "for audit queries (cold path)? Explore whether aggressive snapshotting "
        "(snapshot every 100 events instead of every 1000) keeps most loads "
        "within a snapshot + 100 events, reducing upcaster iterations "
        "significantly. Identify whether the architectural migration cost "
        "(losing full event history, rebuilding audit capability, downtime) "
        "outweighs the performance benefit given your current query patterns "
        "and growth trajectory."
    ),
)

upgrade(
    "MSV-045 - Shared Database Anti-Pattern.md",
    evo=(
        "Shared database became an anti-pattern in the microservices era but "
        "was the standard practice in SOA (2000s). SOA encouraged service "
        "decoupling at the interface level while sharing underlying data stores. "
        "'Integration databases' (shared databases serving multiple applications) "
        "were documented as an enterprise integration pattern (Martin Fowler). "
        "The microservices movement (2012-2015) reacted against this: Sam "
        "Newman's 'Building Microservices' (2015) established 'Database per "
        "Service' as a core principle. The discipline evolved from 'share data, "
        "not code' to 'own data, expose it only through your API.'"
    ),
    tw_principle=(
        "A shared database is a shared contract at the deepest level. A schema "
        "change in one service breaks other services without any API change, "
        "without any interface violation, and without any test failure at the "
        "API level. The database is a hidden API that bypasses all the service "
        "boundaries you thought you had established. Any shared storage between "
        "services (database, cache, filesystem) is a dependency that must be "
        "managed with the same discipline as an explicit API contract."
    ),
    tw_bullets=(
        "- **Shared config files:** Multiple processes reading the same config "
        "file share a hidden contract - a change to the file format affects "
        "all readers without any API change.\n"
        "- **Shared Redis namespaces:** Multiple services writing to the same "
        "Redis key namespace share implicit coupling - a key format change in "
        "one service breaks other services' cache reads.\n"
        "- **Shared Kafka topic schemas:** Multiple services consuming from "
        "the same topic are coupled through the message schema - the same "
        "coupling as shared database schema, at the messaging layer."
    ),
    st=(
        "Teams migrating from a shared database to separate databases often "
        "discover that the shared database was doing more work than they "
        "realised - specifically, acting as the consistency boundary for all "
        "cross-service operations. Removing the shared database removes this "
        "consistency boundary. Teams must then implement explicit eventual "
        "consistency patterns (sagas, outbox, event-driven updates) for every "
        "cross-service data relationship that previously relied on a single "
        "database transaction. The visible complexity of the microservices "
        "system increases during migration - which is the correct sign that "
        "the complexity was always there, just hidden inside the transactions."
    ),
    q1_hint=(
        "Think about what a 4-phase migration looks like concretely: Phase 1 "
        "(identify ownership: determine which service owns which tables, add "
        "API endpoints for each cross-service access pattern currently done "
        "via direct SQL); Phase 2 (dual access: route some cross-service reads "
        "through APIs while keeping the shared DB as fallback); Phase 3 (API "
        "only: remove all direct cross-service SQL, enforce API-only access); "
        "Phase 4 (split databases: move each service's tables to separate "
        "instances). Explore what the rollback strategy is at each phase and "
        "which phase has the highest risk."
    ),
    q2_hint=(
        "Think about what separate schemas in the same PostgreSQL instance "
        "prevents vs what it doesn't prevent: logical isolation (no accidental "
        "JOIN) vs physical isolation. Separate schemas do NOT prevent: (1) a "
        "PostgreSQL instance outage affecting all services simultaneously; "
        "(2) a runaway query from one service consuming all connections; "
        "(3) one service's table growth filling the disk and blocking others' "
        "writes; (4) a DBA granting cross-schema access under operational "
        "pressure. Separate schemas are logical isolation; separate instances "
        "are physical isolation. The choice depends on your operational "
        "failure modes."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Three months after completing migration to "
        "Database per Service, the data team requires real-time analytics "
        "(sub-second latency) joining Order Service, Customer Service, and "
        "Inventory Service data. Design the analytics architecture that meets "
        "the latency requirement without violating data isolation."
    ),
    q3_hint=(
        "Think about what 'sub-second analytics joining 3 service databases' "
        "requires: a read model that has already joined and denormalised the "
        "data from all 3 services, so the analytics query hits a single table. "
        "Explore whether an event-driven analytics store (each service publishes "
        "events to Kafka, a stream processor joins and aggregates into a "
        "denormalised analytics table, queries hit the analytics store) provides "
        "sub-second read latency while maintaining write isolation, and what "
        "consistency lag exists between a service event and the analytics store "
        "update (typically milliseconds to seconds)."
    ),
)

print("\nBatch 4 (MSV-036 to MSV-045) complete.")
