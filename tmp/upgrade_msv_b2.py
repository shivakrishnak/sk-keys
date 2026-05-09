#!/usr/bin/env python3
"""Upgrade MSV-016 through MSV-025 from v2.1 to v3.0."""
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
            text = text.rstrip() + f"\n\n*Hint:* {hint}\n"
            return text
        insert_at = text.rfind("\n\n", q_pos, next_pos)
        if insert_at < 0:
            insert_at = next_pos
        return text[:insert_at] + f"\n\n*Hint:* {hint}" + text[insert_at:]

    c = insert_hint(c, "**Q1.**", "**Q2.**", q1_hint)
    c = insert_hint(c, "**Q2.**", "**Q3.**", q2_hint)
    c = c.rstrip() + f"\n\n{q3_text}\n\n*Hint:* {q3_hint}\n"
    fp.write_text(c, encoding="utf-8")
    print(f"OK: {filename}")


# ────────────────────────────────────────────────────────────────────
# MSV-016 - Aggregate
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-016 - Aggregate.md",
    evo=(
        "The Aggregate pattern was formalised by Eric Evans in \"Domain-Driven "
        "Design\" (2003) as the solution to cross-object invariant enforcement. "
        "Early OO systems tried to keep each individual object valid independently, "
        "but found that business invariants spanning multiple objects were "
        "violated when objects were modified separately. The Aggregate defines a "
        "transactional consistency boundary: all changes within an aggregate "
        "happen in one transaction; changes across aggregates happen through "
        "domain events. In microservices, aggregates became the unit of service "
        "decomposition: each service owns one or more aggregates and their "
        "persistence."
    ),
    tw_principle=(
        "An aggregate is a transactional consistency boundary, not a grouping "
        "of related objects. Objects can be related without requiring transactional "
        "consistency - they belong in different aggregates if they can change "
        "independently. The correct aggregate boundary is the smallest set of "
        "objects that must change atomically to enforce a business invariant. "
        "Making aggregates too large increases contention; making them too small "
        "pushes invariant enforcement outside the transaction boundary."
    ),
    tw_bullets=(
        "- **Database transactions:** A database transaction is an aggregate "
        "boundary at the persistence layer - all operations in the transaction "
        "must succeed or all fail, enforcing consistency across the included "
        "rows.\n"
        "- **UI form validation:** A form that validates all fields before "
        "submission is an aggregate at the UI layer - the form is the consistency "
        "boundary that prevents partial state from being committed.\n"
        "- **Shopping cart:** A Cart + CartItems aggregate enforces invariants "
        "(total within budget, items in stock) across all items together - the "
        "same pattern as a DDD aggregate applied to UI state."
    ),
    st=(
        "The most common Aggregate design mistake is making aggregates too large. "
        "Eric Evans explicitly warns against this: large aggregates lead to "
        "contention (many concurrent operations lock the same aggregate root) "
        "and frequent optimistic concurrency conflicts. The guidance is to make "
        "aggregates as small as possible while still maintaining their invariants. "
        "In practice, most aggregates should contain only 1-3 domain objects. "
        "An Order aggregate containing Order + OrderLines is reasonable; an "
        "Order aggregate containing Order + Customer + Product catalogue is a "
        "design smell that will manifest as write throughput bottlenecks at scale."
    ),
    q1_hint=(
        "Think about what optimistic locking does under high concurrency: many "
        "threads read the same aggregate version, each increments, only one "
        "write succeeds per cycle - the rest fail and retry. At 10,000 concurrent "
        "writers, retry storms can make the aggregate unwriteable at sustained "
        "rates. Explore whether making Comment its own aggregate (separate from "
        "Post) allows comments to be added without locking the Post aggregate, "
        "and how the 1000-comment rule could be enforced as an eventually "
        "consistent read-side check (count domain events, enforce on a domain "
        "service query) rather than a write-side aggregate invariant."
    ),
    q2_hint=(
        "Think about what partial delivery means with the outbox pattern: the "
        "Order aggregate writes OrderConfirmed to an outbox table in the same "
        "transaction as the order commit. A background relay reads the outbox "
        "and delivers to each consumer independently. Explore whether at-least-"
        "once delivery (relay retries until acknowledged) plus consumer-side "
        "idempotency (each consumer deduplicates by event ID before processing) "
        "makes the system resilient to partial delivery without requiring "
        "distributed transactions."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your checkout operation must atomically "
        "validate stock, reserve stock, create an Order aggregate, and clear the "
        "Cart aggregate. These span two aggregates (Cart and Order) and an "
        "external Inventory service. How do you design the checkout transaction "
        "to maintain aggregate consistency without a distributed transaction?"
    ),
    q3_hint=(
        "Think about which operations must be atomic vs which can be eventually "
        "consistent. Explore whether the Cart-to-Order transition can use the "
        "Saga pattern: create the Order atomically (one transaction), then "
        "publish OrderCreated event that triggers Cart clearing and Inventory "
        "reservation as compensatable steps. Identify what the inconsistency "
        "window looks like (briefly unconverted cart, briefly unreserved "
        "inventory) and whether the business can tolerate it."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-017 - Ubiquitous Language
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-017 - Ubiquitous Language.md",
    evo=(
        "Ubiquitous Language was introduced by Eric Evans in \"Domain-Driven "
        "Design\" (2003) as the foundational practice preceding all other DDD "
        "patterns. Evans observed that the most common cause of software defects "
        "was the translation layer between domain expert language and code "
        "language - each translation was an opportunity for misunderstanding. "
        "Alberto Brandolini's Event Storming workshop (2013) turned Ubiquitous "
        "Language discovery into a collaborative practice teams could run without "
        "DDD expertise. The discipline evolved from a design philosophy into "
        "a team practice with specific facilitation techniques."
    ),
    tw_principle=(
        "Language ambiguity is always a hidden defect waiting to manifest. When "
        "two people use the same word to mean different things, they agree in "
        "conversation but diverge in implementation. Establishing a shared, "
        "explicit, written definition for every domain term is defect prevention, "
        "not pedantry. The same principle applies to any shared vocabulary: API "
        "contracts, data schemas, error codes, and event names."
    ),
    tw_bullets=(
        "- **API design:** HTTP status code 422 means different things to "
        "different teams (validation error vs business rule violation). Without "
        "an explicit shared definition, API consumers implement different error "
        "handling strategies for the same response code.\n"
        "- **Data schema:** A column named `status` with values ('A', 'I', 'P') "
        "with no documentation is a Ubiquitous Language violation at the data "
        "layer - the next engineer must guess what each value means.\n"
        "- **Documentation:** A README that uses `user`, `customer`, and "
        "`account` interchangeably creates ambiguity for every engineer who reads "
        "it after the original author leaves."
    ),
    st=(
        "The most damaging consequence of Ubiquitous Language violations is "
        "not bugs - it is invisible divergence. When two teams use the same word "
        "differently, they write code that appears compatible (same type name) "
        "but has different semantics. These defects appear only in production "
        "under specific conditions - when a caller expects one semantic and "
        "receives another. They are particularly hard to find because the code "
        "passes all tests (each team's tests use the team's own definition) and "
        "the type system reports no errors (same type name, compatible interface). "
        "Only end-to-end tests or production incidents reveal the divergence."
    ),
    q1_hint=(
        "Think about how you discover the term the domain genuinely uses: "
        "observe domain experts talking to each other (not to engineers) and "
        "note which term they use unprompted. When experts use multiple terms "
        "interchangeably, ask them to explain the difference - there almost "
        "always is one, and the difference will reveal a domain concept. Explore "
        "whether a Ubiquitous Language glossary maintained in the repository "
        "(linked from code comments and API docs) can serve as the formal "
        "arbiter when experts disagree in conversation."
    ),
    q2_hint=(
        "Think about what `CustomerCreated` means in both the original and new "
        "interpretations: the event name became semantically ambiguous when Sales "
        "changed what triggers it without versioning the event. Explore whether "
        "renaming to `LeadConverted` (a lead that has bought something) vs "
        "`LeadCreated` (any new CRM entry) would make the semantic difference "
        "explicit in the event name, and how consumer-driven contract tests "
        "(Pact) would have caught the semantic change before it reached "
        "the Finance context in production."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your team established a glossary of 50 "
        "domain terms with precise definitions. Three months later, a codebase "
        "audit finds 20 different spellings and synonyms for the same concepts "
        "(`customerEntity`, `CustomerObj`, `client`, `ClientModel`, `user`). "
        "The glossary exists but was ignored. Design a technical enforcement "
        "mechanism that prevents language drift in code without requiring manual "
        "review of every commit."
    ),
    q3_hint=(
        "Think about where language drift can be caught automatically: custom "
        "linting rules that reject banned synonyms (ArchUnit in Java, ESLint "
        "custom rules in TypeScript), code generation from the glossary (domain "
        "objects generated from the canonical glossary so the code IS the "
        "glossary), and PR templates requiring authors to confirm new types match "
        "approved domain terms. Explore whether ArchUnit can express a rule that "
        "all classes in the domain layer must be named using terms from a "
        "configured approved set."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-018 - Anti-Corruption Layer
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-018 - Anti-Corruption Layer.md",
    evo=(
        "The Anti-Corruption Layer (ACL) was introduced by Eric Evans in "
        "\"Domain-Driven Design\" (2003) as the integration pattern for "
        "connecting a new domain model to a legacy or external system without "
        "letting the external model corrupt the new one. Before the ACL concept, "
        "teams integrating with legacy systems would model their new system "
        "using the legacy's data structures and vocabulary - inheriting its "
        "design decisions and constraints. The ACL evolved from a translation "
        "object into a full architectural boundary including adapters (data "
        "translation), facades (interface simplification), and translators "
        "(model conversion)."
    ),
    tw_principle=(
        "Every integration point is a boundary where models can bleed into each "
        "other. Without an explicit translation layer, the external system's "
        "model seeps into your domain, contaminating your vocabulary, your "
        "invariants, and your design decisions. An ACL is a membrane that allows "
        "data to flow while preventing model contamination. The same principle "
        "applies to any system boundary: network protocols, file formats, and "
        "database schemas shared with external teams."
    ),
    tw_bullets=(
        "- **Third-party API integration:** When integrating with a payment "
        "gateway, translate the gateway's `charge`, `refund`, `capture` "
        "operations into your domain's `PaymentAttempted`, `RefundProcessed` "
        "events. Your domain never references the gateway's response format "
        "directly.\n"
        "- **Legacy database access:** A repository layer that translates between "
        "a legacy schema (`customer_type_code` = 1, 2, 3) and your domain model "
        "(`CustomerTier.BASIC`, `PREMIUM`, `ENTERPRISE`) is an ACL at the "
        "persistence layer.\n"
        "- **External event consumption:** A Kafka consumer that translates "
        "partner-published events (using their schema and naming) into your "
        "domain's equivalent events before they enter your processing pipeline "
        "is an ACL at the messaging layer."
    ),
    st=(
        "The most counterintuitive finding about Anti-Corruption Layers is that "
        "they often reveal gaps in the new domain model, not just complexity in "
        "the legacy system. When writing translation logic between a legacy model "
        "and a new domain model, teams frequently discover that the new model "
        "has no clear concept for something the legacy model does - which means "
        "the new model has an incomplete design. The ACL translation code becomes "
        "impossible to write cleanly not because the legacy is badly designed, "
        "but because the new domain model hasn't thought through the concept. "
        "The ACL acts as a specification test for the new domain model's "
        "completeness."
    ),
    q1_hint=(
        "Think about what the ACL's interface to the domain looks like: the "
        "domain service calls a single port interface (`BillingSystemPort`) "
        "without knowing which SAP version is behind it. Explore whether the "
        "Adapter pattern (one Adapter class per SAP version, selected by a "
        "factory configured by company identifier) enables the ACL to route to "
        "either implementation based on a routing rule, keeping the domain "
        "service completely unaware of which SAP version it is talking to."
    ),
    q2_hint=(
        "Think about what adding `FROZEN` to your domain model means downstream: "
        "every API returning `CustomerStatus` must be updated, every "
        "switch/match statement on `CustomerStatus` must handle the new case, "
        "and every event subscriber must handle `FROZEN`. Explore whether the "
        "business rule 'payments are blocked for suspended accounts' should also "
        "apply to FROZEN accounts, and whether silently mapping code 6 to "
        "SUSPENDED creates a hidden defect where frozen accounts have payments "
        "incorrectly blocked or incorrectly allowed."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your ACL between the Orders service and a "
        "legacy ERP system has grown to 800 lines of translation logic over 18 "
        "months and is the most defect-prone file in the codebase. Three "
        "developers introduced bugs in the last quarter. What architectural "
        "improvements to the ACL would reduce defect rate without a "
        "full rewrite?"
    ),
    q3_hint=(
        "Think about what makes the 800-line ACL hard to change correctly: "
        "implicit knowledge about the legacy schema embedded in procedural code, "
        "no tests that verify translation against real legacy data shapes, and "
        "no single place where the mapping is declared (logic scattered across "
        "methods). Explore whether a declarative mapping approach (explicit "
        "mapping tables or schema-first translation with contract tests against "
        "the legacy API) would make the translation logic testable and "
        "auditable, so defects are caught at test time rather than in production."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-019 - Strangler Fig Pattern
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-019 - Strangler Fig Pattern.md",
    evo=(
        "The Strangler Fig pattern was named and popularised by Martin Fowler in "
        "2004, drawing the analogy from the strangler fig tree (Ficus aurea) "
        "that grows around a host tree and eventually replaces it. While the "
        "concept of incremental system replacement existed before, Fowler gave "
        "it a memorable name and a clear implementation approach: add new "
        "functionality in the new system, route via a facade, gradually migrate "
        "old functionality, retire the old system when fully replaced. The "
        "pattern became the dominant migration strategy as big-bang rewrites "
        "continued to fail at high rates."
    ),
    tw_principle=(
        "Incremental migration is safer than complete migration because each "
        "step is independently validatable and reversible. The Strangler Fig's "
        "core innovation is not the routing facade - it is the discipline of "
        "never removing the old system until the new system has proven "
        "equivalence in production traffic. The same principle applies to any "
        "system replacement: run both systems in parallel, compare outputs, "
        "migrate traffic gradually."
    ),
    tw_bullets=(
        "- **Database schema migration (Expand-Contract):** Add new columns "
        "alongside old (expand), migrate reads and writes to new columns, then "
        "remove old columns (contract). Never drop a column at the same time as "
        "adding a replacement - the same wrap-and-redirect as Strangler Fig.\n"
        "- **API versioning:** Maintain v1 and v2 of an API simultaneously, "
        "migrate clients to v2 gradually, retire v1 only when all clients have "
        "migrated.\n"
        "- **UI framework migration:** Render React components inside a jQuery "
        "page, gradually replace jQuery sections with React, remove jQuery when "
        "the last section is replaced - incremental, parallel operation, "
        "retire-last."
    ),
    st=(
        "The Strangler Fig pattern fails in a specific way teams rarely "
        "anticipate: the old system never fully dies. The \"remaining 20%\" that "
        "was always going to be \"migrated next quarter\" gradually becomes the "
        "permanent state of a migration that never completes. The legacy "
        "branches accumulate new features (product teams don't wait for the "
        "migration to complete), making them progressively harder to migrate. "
        "Successful Strangler Fig migrations require a hard business commitment "
        "to feature freezes on the legacy system during the migration window - "
        "otherwise the migration is chasing a moving target and will never "
        "catch up."
    ),
    q1_hint=(
        "Think about the failure modes of each approach under high load: "
        "(A) calling the monolith's /customers API adds network latency and "
        "creates synchronous coupling (monolith unavailability = Orders failure); "
        "(B) dual-write requires atomicity across two databases (distributed "
        "transaction risk, or 2-phase-commit complexity); (C) CDC introduces "
        "replication lag (Orders may have stale customer data). Explore which "
        "failure modes are tolerable for your specific customer data usage "
        "patterns and whether CDC's eventual consistency is acceptable during "
        "the migration window."
    ),
    q2_hint=(
        "Think about what '0.3% divergence' means in absolute terms at your "
        "traffic volume and whether the divergence is always the same request "
        "patterns or random. Explore the 'golden record' approach: run both "
        "implementations in shadow mode, capture all diverging cases, and "
        "present each to domain experts to determine the correct business rule. "
        "The correct implementation is the one that matches the business intent, "
        "not necessarily the monolith (which may have bugs) or the new service "
        "(which may have missed edge cases)."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your Strangler Fig facade routes 10% of "
        "traffic to a new service and 90% to the monolith. After 2 weeks, the "
        "new service has P99 latency 40ms higher than the monolith. Users on "
        "the 10% path have a slightly worse experience. Should you pause "
        "migration and fix latency before proceeding, or accept the regression?"
    ),
    q3_hint=(
        "Think about what 40ms P99 means in user experience terms (below the "
        "100ms human perception threshold?) and whether the latency comes from "
        "the facade's routing overhead (will disappear when migration completes) "
        "or the new service's design (requires architectural fixes). Explore "
        "whether running shadow mode (both old and new receive traffic, new "
        "results are discarded) while profiling the latency difference lets you "
        "diagnose the root cause before deciding whether to pause or proceed."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-020 - Service Registry
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-020 - Service Registry.md",
    evo=(
        "Service registries emerged as dynamic IP assignment made static "
        "service configuration unworkable. In the 1990s, service endpoints "
        "were hard-coded in configuration files - manageable with tens of "
        "services on fixed infrastructure. Netflix's cloud migration "
        "(2008-2012) created thousands of auto-scaling instances with dynamic "
        "IPs, motivating Eureka (AP registry, client-side discovery). "
        "HashiCorp Consul (2014) generalised the registry to multiple protocols "
        "and prioritised CP consistency. Kubernetes' built-in service discovery "
        "(2015) abstracted the registry into the platform, making it transparent "
        "to applications."
    ),
    tw_principle=(
        "Service discovery is an infrastructure concern that should be invisible "
        "to services. A service should not know whether it is using DNS, a "
        "registry, or a service mesh - it should call a name and have the "
        "infrastructure resolve it to a healthy instance. When discovery logic "
        "leaks into application code (Eureka client JAR embedded in every "
        "service), every service is coupled to a specific discovery "
        "implementation that is hard to migrate."
    ),
    tw_bullets=(
        "- **DNS:** DNS is service discovery for the internet - a name-to-IP "
        "mapping that is cached, replicated, and eventually consistent. The "
        "principle (resolve name to address) is identical to a service registry.\n"
        "- **Kubernetes Services:** A Kubernetes Service maps a logical service "
        "name to a set of pod IPs, updated dynamically as pods come and go - "
        "service discovery built into the platform, transparent to applications.\n"
        "- **Load balancers:** A load balancer that forwards to registered "
        "backends is a server-side service registry - the client only knows the "
        "load balancer's address, not the individual backends."
    ),
    st=(
        "Eureka's 'self-preservation mode' - where it refuses to deregister "
        "instances during suspected network partitions - has caused more "
        "production incidents at Netflix than it has prevented. The mode was "
        "designed to avoid falsely deregistering healthy instances during brief "
        "network glitches. In practice, it causes stale routing: a service "
        "that has genuinely gone down continues receiving traffic for minutes "
        "or hours. Netflix's own documentation now recommends that most "
        "production systems disable self-preservation mode and implement "
        "proper client-side circuit breakers to handle instances that the "
        "registry fails to deregister promptly."
    ),
    q1_hint=(
        "Think about what self-preservation mode is optimising for: it chooses "
        "'retain stale data' over 'remove possibly valid data' - a deliberate "
        "AP trade-off. The circuit breaker should compensate for stale registry "
        "data by detecting that specific instances are unhealthy via failure rate "
        "measurement (not registry state) and opening the circuit to those "
        "instances independently of what the registry reports. Explore how "
        "Resilience4j per-instance circuit breakers (keyed by instance IP, not "
        "service name) provide local failure knowledge that the registry cannot."
    ),
    q2_hint=(
        "Think about what a bridge component must do: receive requests from "
        "Eureka-discovered services, forward to Consul-registered services, and "
        "register in both systems so both discovery modes can find it. Explore "
        "whether an Envoy sidecar registered in both Eureka and Consul can act "
        "as the bridge without application code changes, and what the failure "
        "mode is if the bridge instance itself becomes unavailable during "
        "the migration."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your team must choose between a centralised "
        "service registry (Consul) and Kubernetes-native service discovery "
        "(kube-proxy ClusterIP + CoreDNS) for a 150-service system running "
        "entirely on Kubernetes. What criteria determine which is the better "
        "choice?"
    ),
    q3_hint=(
        "Think about what Kubernetes-native discovery already provides (DNS-"
        "based name resolution, ClusterIP, automatic pod health registration) "
        "vs what Consul adds (cross-cluster discovery, non-Kubernetes workloads, "
        "service mesh features, richer health check options). Explore whether "
        "the 150-service system has any workloads outside Kubernetes that "
        "require Consul's cross-environment capabilities - if not, Kubernetes-"
        "native discovery covers 95% of needs with zero additional infrastructure "
        "to operate."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-021 - Service Discovery
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-021 - Service Discovery.md",
    evo=(
        "Service discovery evolved from DNS (1983) to purpose-built registries "
        "as microservices introduced dynamic scaling and health checking "
        "requirements DNS could not meet. DNS TTL (typically 30-300 seconds) "
        "was too slow to propagate pod failures in high-traffic systems. "
        "Netflix's Eureka (2012), HashiCorp Consul (2014), and Kubernetes' "
        "built-in discovery (2015) each addressed different trade-offs between "
        "consistency, availability, and operational simplicity. The discipline "
        "evolved from 'hard-code service endpoints' to 'name services, discover "
        "instances dynamically, health-check continuously.'"
    ),
    tw_principle=(
        "Service discovery is the runtime equivalent of a phone book: names "
        "are stable, addresses change. The valuable invariant is that callers "
        "use names (stable) rather than addresses (ephemeral). When services "
        "are called by name, the infrastructure can change what the name "
        "resolves to without callers needing to be updated or redeployed."
    ),
    tw_bullets=(
        "- **Database failover:** Connection pool libraries discover the database "
        "leader by hostname (db.primary.internal) and reconnect when the name "
        "resolves to a new IP after a failover - service discovery for "
        "databases.\n"
        "- **CDN geo-routing:** CDN DNS routes client requests to the nearest "
        "edge node by resolving the same hostname to different IPs based on "
        "client geography - service discovery applied to content delivery.\n"
        "- **Email delivery:** MX records in DNS are service discovery for mail "
        "servers - a domain name resolves to the mail server responsible for "
        "receiving email, changeable without affecting senders."
    ),
    st=(
        "The most common service discovery failure mode is not the discovery "
        "mechanism itself failing - it is the absence of health checking. A "
        "registry that faithfully reports all registered instances (including "
        "those that are running but serving incorrectly - deadlocked, out of "
        "memory, returning 500s for every request) is worse than no registry: "
        "it routes traffic to instances that will fail, consuming request "
        "budgets and masking the real problem. Modern service discovery combines "
        "registration with continuous health monitoring - a service's registration "
        "and its health status are inseparable in correctly designed systems."
    ),
    q1_hint=(
        "Think about what happens when a caller receives a mix of v1 and v2 "
        "responses and parses them with a v1 parser: optional new fields are "
        "ignored (backward compatible), required new fields cause parse errors "
        "(breaking), removed fields cause null pointer exceptions (breaking). "
        "Explore whether the API contract should be versioned at the endpoint "
        "URL level (/v2/payments) or at the service instance level (discovery "
        "tags indicating API version), and what rolling deployment guarantees "
        "that callers never receive a mix of versions simultaneously."
    ),
    q2_hint=(
        "Think about what the registry cannot know: instances may be registered "
        "as healthy (heartbeats succeeding) but not actually serving requests "
        "(thread pool exhausted, deadlocked, dependency down). The 5 most likely "
        "causes (in order): (1) payment service thread pools exhausted by slow "
        "downstream; (2) network path between order and payment is degraded, "
        "not severed; (3) order service timeout shorter than payment response "
        "time; (4) payment's database or external API unavailable; (5) TLS "
        "certificate expiry on inter-service mTLS. Diagnostic: `kubectl exec "
        "-it <pod> -- curl localhost:8080/actuator/health`, check thread pool "
        "metrics, test connectivity with nc."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Two microservices in different Kubernetes "
        "clusters (different cloud regions) must discover and call each other. "
        "Kubernetes DNS-based service discovery does not work across clusters. "
        "Design the cross-cluster service discovery strategy."
    ),
    q3_hint=(
        "Think about the three main options: (1) expose via LoadBalancer "
        "(external IP, reachable cross-cluster but publicly visible - security "
        "risk); (2) service mesh with cross-cluster support (Istio multicluster, "
        "Linkerd multicluster - mutual TLS, service-level routing, but "
        "operational complexity); (3) centralised registry (Consul) registered "
        "in both clusters. Explore what the latency, security, and operational "
        "complexity trade-offs are for each, and whether the cross-cluster "
        "calls are synchronous (latency-sensitive) or asynchronous (can tolerate "
        "retry-level network handling)."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-022 - Client-Side vs Server-Side Discovery
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-022 - Client-Side vs Server-Side Discovery.md",
    evo=(
        "The client-side vs server-side discovery distinction emerged as "
        "architects recognised that the placement of load balancing intelligence "
        "has fundamental implications for failure modes and operational "
        "complexity. Netflix's Ribbon (2012) established client-side load "
        "balancing for JVM services. AWS ELB (2009) and ALB (2016) established "
        "server-side discovery as a managed service pattern. Kubernetes' kube-"
        "proxy (2014) made server-side discovery a platform concern. The "
        "discipline evolved from 'choose a load balancer' to understanding the "
        "implications of routing intelligence placement for observability, "
        "failure handling, and language ecosystem portability."
    ),
    tw_principle=(
        "The choice of where routing intelligence lives determines where "
        "complexity accumulates. Client-side routing distributes intelligence "
        "across every service (each contains load balancing, health checking, "
        "circuit breaking logic), distributing complexity but making consistency "
        "across language ecosystems difficult. Server-side routing centralises "
        "intelligence in the proxy/load balancer, simplifying services but "
        "creating a single component that must handle all routing decisions."
    ),
    tw_bullets=(
        "- **Database connection pooling:** PgBouncer (server-side connection "
        "pooling) vs application-level connection pooling (client-side) is the "
        "same architectural choice at the database layer - where does the "
        "pooling and routing logic live?\n"
        "- **API gateways:** An API gateway is server-side routing for external "
        "clients - all routing, authentication, and rate limiting logic "
        "centralised in one place rather than distributed across calling clients.\n"
        "- **Service meshes:** A service mesh (Envoy sidecar) is a hybrid: "
        "server-side routing logic deployed with each service instance, "
        "combining the observability of server-side with the isolation of "
        "client-side."
    ),
    st=(
        "Netflix's adoption of client-side load balancing (Ribbon) was driven "
        "by a specific AWS constraint in 2010: Elastic Load Balancer did not "
        "support fine-grained per-instance health checking at the speed Netflix "
        "needed. Netflix built Ribbon to run inside each service, combining "
        "Eureka registry data with per-call failure tracking. By 2022, Netflix "
        "had migrated away from Ribbon to gRPC with Envoy sidecars - "
        "essentially moving from client-side to server-side routing. The full "
        "circle took 12 years and was driven by the recognition that distributed "
        "routing logic in thousands of service instances is harder to observe "
        "and update than centralised routing logic in a managed sidecar."
    ),
    q1_hint=(
        "Think about what iptables-based kube-proxy does: it writes O(n^2) "
        "iptables rules for n services, and each packet traversal scans rules "
        "linearly until a match is found. IPVS uses a hash table for O(1) "
        "rule lookup. Cilium eBPF bypasses iptables entirely, processing "
        "packets in the XDP layer before they reach the TCP/IP stack. Explore "
        "the operational trade-offs: iptables (universal support, complex at "
        "scale), IPVS (faster matching, still kernel network stack), eBPF/Cilium "
        "(lowest latency, requires kernel 4.9+ and eBPF expertise to debug)."
    ),
    q2_hint=(
        "Think about the discovery model differences that explain the timing "
        "gap: Spring Cloud Ribbon (client-side) marks an instance unhealthy on "
        "the first failed call - detection is per-call, sub-second. Consul "
        "HTTP client (server-side) depends on health check polling intervals "
        "(default 10-second poll) plus deregistration TTL (often 30 seconds). "
        "The 90-second vs 15-second gap maps directly to this polling interval "
        "difference. Explore whether standardising both on Envoy sidecar with "
        "unified health check configuration eliminates the timing discrepancy "
        "independent of language."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** You are building a polyglot system with "
        "services in Java, Python, Go, and Node.js that all need load balancing, "
        "circuit breaking, retries, and distributed tracing. Should you implement "
        "these as client-side libraries in each language's ecosystem, or adopt "
        "a service mesh (Envoy sidecar) for server-side consistency? What are "
        "the trade-offs?"
    ),
    q3_hint=(
        "Think about the implementation cost of client-side libraries per "
        "language: Java (Resilience4j + Spring Cloud), Python (Tenacity + custom "
        "retry), Go (go-resiliency), Node (opossum circuit breaker) - each has "
        "different configuration syntax, behaviour at edge cases, and "
        "observability output. Explore whether a service mesh enforces consistent "
        "retry/timeout/circuit breaking behaviour across all 4 languages from "
        "a single Envoy config, and what the operational overhead of managing "
        "Envoy sidecars at scale looks like compared to the inconsistency risk "
        "of 4 different client library ecosystems."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-023 - Health Check Patterns
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-023 - Health Check Patterns.md",
    evo=(
        "Health check patterns evolved from simple process monitoring (is the "
        "process running?) to semantic health checking (is the process serving "
        "requests correctly?) as distributed systems proved that running "
        "processes could still be unhealthy. The Liveness vs Readiness "
        "distinction was formalised in Kubernetes 1.0 (2015) and became an "
        "industry standard. The three-tier health check (Liveness, Readiness, "
        "Startup) was standardised in Kubernetes 1.16 (2019). Spring Boot "
        "Actuator's `/health` endpoint (2014) standardised the HTTP health "
        "interface. The discipline evolved from 'is it running?' to 'is it "
        "ready?', 'is it live?', and 'are its dependencies healthy?'"
    ),
    tw_principle=(
        "A health check that depends on external systems is a liability, not "
        "an asset. When a database goes down, all services that include database "
        "connectivity in their readiness check simultaneously become unhealthy "
        "and are removed from routing - even if they could serve cached data "
        "or degraded responses. Health checks should answer: 'Can this specific "
        "instance serve requests right now?' - not 'Are all my dependencies "
        "healthy?'"
    ),
    tw_bullets=(
        "- **Cache warm-up:** A readiness probe that waits for a cache to be "
        "populated before marking a pod ready prevents requests from hitting a "
        "pod with an empty cache - the same principle of 'ready to serve good "
        "responses' applied to data loading state.\n"
        "- **Circuit breaker state:** A service with an open circuit breaker "
        "could mark itself as 'degraded' (live but not ready for full traffic) "
        "- health checking that reflects current capability, not just process "
        "state.\n"
        "- **Dependency monitoring:** A monitoring dashboard that shows the "
        "health of each dependency independently (not just 'the service is "
        "healthy') applies the same disaggregated health principle to "
        "observability."
    ),
    st=(
        "Kubernetes health checks have a subtle failure mode most teams discover "
        "in production: if a readiness probe depends on a database and the "
        "database has a brief outage, all pods fail their readiness probe "
        "simultaneously. Kubernetes removes all of them from the service "
        "endpoints, and the load balancer returns 503 for all requests. When "
        "the database recovers, all pods pass their readiness probe "
        "simultaneously - the thundering herd of reconnecting clients often "
        "overwhelms the database again. The solution is to make readiness probes "
        "independent of database connectivity and use circuit breakers to handle "
        "database unavailability at the request level, keeping pods in rotation "
        "to serve non-database-dependent requests."
    ),
    q1_hint=(
        "Think about what the readiness probe semantics should be: it answers "
        "'should this pod receive traffic right now?' During a database outage, "
        "is 0 pods in rotation (all fail readiness) better or worse than all "
        "pods returning 503 for DB-dependent requests? Explore whether a "
        "'degraded' readiness mode (pod accepts non-DB-dependent requests when "
        "DB is down) preserves partial service availability, and whether "
        "Kubernetes supports routing different request types to different "
        "service endpoints based on pod health state."
    ),
    q2_hint=(
        "Think about what the liveness probe semantics should be: it answers "
        "'is this process in a healthy state to make progress?' For a slow "
        "memory leak, the failure condition is continuous (GC pauses growing) "
        "not binary (not crashed). Explore whether a custom liveness endpoint "
        "that measures heap usage and GC pause P99 and returns 503 above "
        "thresholds (heap > 85%, GC pause P99 > 500ms) would trigger restart "
        "at the right time, and what consecutive-failure count prevents "
        "false positives during brief but normal GC events."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A microservice depends on 3 external "
        "services: a primary database (critical), a cache (optional, degrades "
        "gracefully without it), and an analytics service (fire-and-forget). "
        "Design the health check strategy that correctly represents this "
        "service's ability to serve requests under each dependency failure "
        "scenario, specifying liveness, readiness, and startup probe "
        "configurations."
    ),
    q3_hint=(
        "Think about which dependency belongs in which probe: startup (is the "
        "app initialised - includes DB schema validation, initial cache warm-up); "
        "readiness (should it receive traffic - primary DB reachable and "
        "connection pool healthy; cache: log degraded but remain ready); liveness "
        "(is it still making progress - check for deadlocks and OOM, not "
        "dependencies). Explore whether the analytics service should appear in "
        "any health check at all (it is fire-and-forget) or just in application "
        "metrics (queue depth, failure rate)."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-024 - Inter-Service Communication
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-024 - Inter-Service Communication.md",
    evo=(
        "Inter-service communication patterns evolved from RPC (1970s) through "
        "CORBA and SOAP's 'distributed objects' illusion (1990s) to REST's "
        "resource-oriented simplicity (Roy Fielding, 2000) and gRPC's efficient "
        "binary protocol (Google, 2015). Each wave tried to make network calls "
        "look like in-process calls - and each wave eventually recognised this "
        "was the wrong abstraction. The 'Fallacies of Distributed Computing' "
        "(Peter Deutsch, 1994) articulated why: the network is not reliable, "
        "latency is not zero, bandwidth is not infinite. Modern inter-service "
        "design accepts these as invariants and designs explicitly for async, "
        "retry, timeout, and circuit breaking."
    ),
    tw_principle=(
        "Every synchronous inter-service call adds latency and expands the "
        "failure surface. Total latency of a synchronous chain is the sum of all "
        "service latencies plus network overhead. Failure probability of a chain "
        "is approximately 1-(1-p)^n for n services with individual failure "
        "probability p. These two formulas should drive every inter-service "
        "design decision: minimise chain length and replace synchronous calls "
        "with async messaging wherever the caller can proceed without "
        "an immediate response."
    ),
    tw_bullets=(
        "- **Database N+1 queries:** One query per item in a list is the same "
        "failure mode as a synchronous inter-service call per item - each adds "
        "latency multiplicatively. The solution is the same: batch or aggregate.\n"
        "- **Frontend API design:** A frontend making 10 sequential API calls "
        "to assemble a page is the same pattern as a microservice making 10 "
        "sequential downstream calls. The BFF pattern solves both by aggregating "
        "on the server side.\n"
        "- **Third-party API integration:** A service that synchronously calls "
        "an external API on every user request is coupled to that API's "
        "availability and latency. Async event-driven processing (background "
        "worker handles the external call) decouples service availability from "
        "the external API."
    ),
    st=(
        "gRPC - which uses HTTP/2 and Protocol Buffers and is significantly "
        "faster than REST+JSON in benchmarks - is often slower in practice at "
        "the system level. gRPC's complexity (proto schema compilation, streaming "
        "semantics, HTTP/2 multiplexing) introduces operational overhead that "
        "REST's simplicity avoids. REST API failures are debuggable with curl; "
        "gRPC failures require proto-aware tools. REST APIs can be inspected in "
        "browser developer tools; gRPC cannot. At high throughput where payload "
        "serialisation is the bottleneck, gRPC wins clearly. At moderate "
        "throughput where debugging and operational overhead dominate, REST is "
        "often the pragmatic winner despite benchmark disadvantage."
    ),
    q1_hint=(
        "Think about what 'notifications must be reliable' requires: the "
        "confirmation email must eventually be sent even if the notification "
        "service is slow or briefly unavailable. Explore whether publishing "
        "an `OrderConfirmed` event to a durable message queue (Kafka, SQS) "
        "and having the notification service consume asynchronously decouples "
        "checkout latency from email delivery latency, and what happens to "
        "events if the notification service is down for an hour (accumulate "
        "in the queue, processed automatically on recovery)."
    ),
    q2_hint=(
        "Think about what 'immediate, safe response' means: the passenger needs "
        "confirmation their request is accepted and being processed - not that "
        "a driver is already assigned. Explore whether a two-phase response "
        "(immediate: 'Ride request accepted, ID 12345' followed by async push "
        "notification: 'Driver assigned, ETA 4 minutes') satisfies the UX "
        "requirement without requiring synchronous driver matching, and what "
        "the cancellation flow is if no driver becomes available within the "
        "expected window."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Every inter-service call that modifies "
        "financial state must be logged with full request/response context for "
        "regulatory compliance. What inter-service communication pattern ensures "
        "auditability without requiring each of 40 services to implement "
        "audit logging individually?"
    ),
    q3_hint=(
        "Think about where the audit intercept can be placed: in each service "
        "(highest fidelity, highest implementation overhead), in the service "
        "mesh sidecar (captures all inter-service traffic automatically at "
        "network level, but may miss in-service state changes), or as explicit "
        "domain events published per financial operation (explicit, versioned, "
        "but requires per-service implementation). Explore whether service mesh "
        "access logs + distributed tracing capture enough context for regulatory "
        "compliance, or whether the compliance requirement needs application-"
        "level event sourcing with immutable audit log storage."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-025 - Synchronous vs Async Communication
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-025 - Synchronous vs Async Communication.md",
    evo=(
        "Synchronous inter-service communication was the default assumption of "
        "early SOA (SOAP-based, 2000s). Async messaging was considered complex "
        "and reserved for legacy system integration. The microservices movement "
        "(2014-2016) and event-driven architecture renewed interest in async "
        "as teams discovered that synchronous coupling was the primary cause "
        "of cascading failures. Chris Richardson's \"Microservices Patterns\" "
        "(2018) systematised async communication as the preferred default. "
        "The discipline evolved from 'sync by default, async for legacy' to "
        "'async by default, sync only when the caller genuinely needs an "
        "immediate response.'"
    ),
    tw_principle=(
        "Choose synchronous communication only when the caller genuinely cannot "
        "proceed without the response. The test is: 'If the downstream service "
        "is unavailable for 30 seconds, should the caller fail immediately or "
        "queue the request and proceed?' If the answer is 'queue and proceed,' "
        "async is correct. If the answer is 'the caller cannot serve the user "
        "without this response,' sync is correct. Sync creates coupling; async "
        "creates decoupling at the cost of operational complexity."
    ),
    tw_bullets=(
        "- **Database writes vs reads (CQRS):** A CQRS system separates "
        "synchronous writes (caller needs acknowledgement) from asynchronous "
        "read model updates (caller doesn't wait for the read model to update) "
        "- the same sync/async decision at the persistence layer.\n"
        "- **Email sending:** Sending a confirmation email is async by nature - "
        "the user doesn't wait for the SMTP connection. Yet many applications "
        "make it synchronous, coupling user response time to email API latency.\n"
        "- **Batch processing:** Processing records synchronously one-at-a-time "
        "is the synchronous pattern. Enqueuing all records for parallel worker "
        "processing is the async pattern - same work, different latency and "
        "resilience characteristics."
    ),
    st=(
        "The most counterintuitive finding about async messaging is that it does "
        "not inherently improve system reliability - it changes where unreliability "
        "is visible. A synchronous system fails immediately and visibly (the "
        "caller gets a 500 error). An async system accumulates failures invisibly "
        "(messages queue up, consumer lag grows). A broker outage in a synchronous "
        "system causes immediate, visible, bounded downtime. A broker outage in "
        "an async system causes invisible, accumulating lag that may take hours "
        "to drain after recovery - during which the system appears to work but "
        "is progressively more delayed. Async resilience requires explicit lag "
        "monitoring, consumer health tracking, and dead-letter queue management "
        "that synchronous systems do not need."
    ),
    q1_hint=(
        "Think about what 'eventually shows all transfers' requires for "
        "durability: TransferCompleted events must be durable even if analytics "
        "is down for 2 hours. Explore whether publishing TransferCompleted to "
        "a durable queue (Kafka with replication factor 3, retention 24 hours) "
        "and having analytics consume asynchronously ensures zero data loss "
        "without blocking the transfer operation, and what consumer lag "
        "monitoring alert thresholds should be set (alert at 5 min behind, "
        "page at 30 min behind)."
    ),
    q2_hint=(
        "Think about what exactly-once semantics requires at the consumer: "
        "idempotent producers prevent duplicate writes to the Kafka broker, but "
        "duplicate delivery to consumers still occurs at consumer group "
        "rebalances. Explore whether consumer-side idempotency (each payment "
        "event has a unique `PaymentEventId`; consumer checks if this ID was "
        "already processed before writing state) combined with careful offset "
        "management (commit offset only after successful state persistence) "
        "eliminates the duplicate/out-of-order visible status issue."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A team migrates checkout from synchronous "
        "HTTP calls (checkout → payment → inventory → notification) to "
        "event-driven (checkout publishes `OrderCreated`, each service "
        "consumes and publishes its own events). Six months later, an engineer "
        "asks: 'How do I know if a specific order from 3 days ago was fully "
        "processed? The monolith had a single SQL query; now I need to query "
        "4 services.' Design the observability approach."
    ),
    q3_hint=(
        "Think about what 'order processing state' means in an event-driven "
        "system: it is the aggregate of all events published and consumed for "
        "a specific order ID. Explore whether a dedicated Order Status service "
        "(subscribes to all order-related events, maintains an aggregate view "
        "of each order's processing state in a queryable store) provides the "
        "single view the engineer needs - and whether this is exactly the CQRS "
        "read model pattern applied to operational visibility rather than "
        "user-facing queries."
    ),
)

print("\nBatch 2 (MSV-016 to MSV-025) complete.")
