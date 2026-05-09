#!/usr/bin/env python3
"""Upgrade MSV-026 through MSV-035 from v2.1 to v3.0."""
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
    "MSV-026 - API Gateway (Microservices).md",
    evo=(
        "API Gateways emerged from the need to provide a unified entry point "
        "to microservices after teams discovered that client-to-service "
        "communication needs differed from service-to-service. The original "
        "reverse proxy (nginx, HAProxy) provided routing but no application-"
        "level features. Netflix Zuul (2013) and Kong (2015) added "
        "authentication, rate limiting, and transformation. AWS API Gateway "
        "(2015) made it a managed service. The discipline evolved from 'single "
        "entry point for routing' to 'policy enforcement point' for all "
        "inbound traffic: auth, rate limiting, SSL termination, and "
        "request transformation."
    ),
    tw_principle=(
        "An API gateway is the policy enforcement point for all external "
        "traffic. It centralises cross-cutting concerns that would otherwise "
        "be implemented redundantly in every service. The same principle "
        "applies at multiple infrastructure layers: each layer enforces "
        "policies without requiring application code changes."
    ),
    tw_bullets=(
        "- **WAF (Web Application Firewall):** Inspects all incoming traffic "
        "for attack patterns before it reaches any service - the same cross-"
        "cutting policy enforcement as an API gateway, at the security layer.\n"
        "- **CDN:** Handles caching, compression, and geographic routing before "
        "requests reach the origin - an API gateway for content delivery.\n"
        "- **Service mesh ingress gateway:** The Istio/Linkerd ingress gateway "
        "is an API gateway at the edge of the service mesh, enforcing mesh "
        "policies for all external-to-mesh traffic."
    ),
    st=(
        "API gateways were sold as the 'single entry point' that would simplify "
        "microservices architectures. In practice, they became a source of "
        "latency, operational overhead, and deployment bottlenecks. Every "
        "cross-cutting concern added to the gateway adds latency to every "
        "request through it. A gateway doing JWT validation + rate limiting + "
        "request transformation + circuit breaking + response caching can add "
        "20-50ms to every request. The backend services are distributed but the "
        "gateway is a monolith: all traffic flows through it, all configuration "
        "changes require gateway deployment, and all gateway bugs affect all "
        "services. Many mature microservices teams now advocate for a 'thin "
        "gateway' (routing and SSL only) and push cross-cutting concerns to "
        "service meshes."
    ),
    q1_hint=(
        "Think about what JWKS caching actually caches: the public key set "
        "used to verify JWT signatures. A cached public key remains valid until "
        "the auth server rotates keys - which happens infrequently (hours to "
        "days). Explore whether caching with a short TTL (1-5 minutes) plus "
        "forced cache refresh on signature verification failure provides the "
        "performance benefit while limiting the window during which a token "
        "signed by a revoked key could still be accepted."
    ),
    q2_hint=(
        "Think about what the three client types actually need differently: "
        "mobile (smaller payloads, bandwidth-sensitive, offline sync), web "
        "(full data, server-side rendering support), third-party (stable "
        "versioned contract, per-client rate limits). Explore whether these "
        "differences justify three separate gateway deployments (3x operational "
        "overhead: deployment, monitoring, certificates) or whether a single "
        "gateway with per-client-type response transformation achieves the same "
        "outcome at lower operational cost."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A new compliance requirement adds a PII "
        "detection check to every request through your API gateway. Benchmarking "
        "shows the check adds 15ms per request. At 50,000 req/s, this creates "
        "significant additional load. Design the compliance enforcement strategy "
        "that meets the requirement without degrading gateway performance."
    ),
    q3_hint=(
        "Think about whether every request needs PII inspection synchronously "
        "or whether async inspection of request logs satisfies the compliance "
        "requirement. Explore whether sampling (inspect 1% of requests, flag "
        "violations for remediation), endpoint exclusion (based on data "
        "classification, exclude endpoints known to carry no PII), and moving "
        "the check to the service level (each service inspects its own payload) "
        "provide compliance coverage without the gateway-level latency impact."
    ),
)

upgrade(
    "MSV-027 - Backend for Frontend (BFF).md",
    evo=(
        "The Backend for Frontend pattern was coined by Sam Newman in 2015 to "
        "address a single API being forced to serve multiple client types with "
        "conflicting needs. The pattern emerged from Netflix's experience with "
        "TV, mobile, and web clients all hitting the same API and receiving more "
        "data than any individual client needed. The BFF provides a client-"
        "specific API layer, owned by the frontend team, that aggregates and "
        "transforms backend service calls to match each client's specific needs. "
        "The discipline evolved from 'one API for all' to 'one API per client "
        "type' - with the BFF as the translation layer."
    ),
    tw_principle=(
        "Build client-specific APIs, not one-size-fits-all APIs. An API "
        "optimised for mobile (minimal data, offline sync) is different from "
        "an API optimised for web (rich data, server-side state), which is "
        "different from a third-party API (stable versioned contract, rate "
        "limited). Serving all clients from one API creates an API suboptimal "
        "for all of them. The BFF extends the 'right tool for the job' principle "
        "to API layer design."
    ),
    tw_bullets=(
        "- **Database query optimisation:** A reporting query (full historical "
        "data) and an OLTP query (current state, single record) require "
        "different indexes and query strategies - the BFF pattern applied to "
        "data access layer design.\n"
        "- **UI component libraries:** A mobile component library (touch-"
        "optimised, minimal) and a desktop library (keyboard-optimised, "
        "feature-rich) serve different client types with different trade-offs "
        "- the BFF pattern applied to frontend component design.\n"
        "- **SDK design:** An embedded device SDK (minimal footprint) vs a web "
        "application SDK (feature-rich) serves different client types with "
        "different constraints - the BFF pattern applied to client library "
        "design."
    ),
    st=(
        "The Backend for Frontend pattern has a hidden failure mode teams "
        "discover 12-18 months after adoption: BFF teams start duplicating "
        "backend business logic in their BFFs. The Mobile BFF calculates "
        "discounts. The Web BFF calculates discounts with slightly different "
        "rules. Six months later, the two BFFs diverge in their discount "
        "calculations and customers see different prices on mobile vs web. "
        "The BFF pattern requires strict discipline: BFFs should only aggregate "
        "and transform - never implement business logic. Business logic must "
        "live in backend services, consumed by all BFFs via API."
    ),
    q1_hint=(
        "Think about what cache coherence means when two BFFs have separate "
        "caches of the same underlying data: when the transaction service "
        "updates a record, both Mobile BFF cache and Web BFF cache must be "
        "invalidated simultaneously. Explore whether a domain event "
        "`TransactionUpdated` published by the transaction service and consumed "
        "by both BFFs for cache invalidation solves the coherence problem, and "
        "whether pushing caching to the transaction service (shared cache, "
        "single invalidation path) eliminates the two-BFF coherence complexity "
        "entirely."
    ),
    q2_hint=(
        "Think about what differs between internal and Partner BFF: internal "
        "(coordinate changes via Slack, can break and fix same day; no SLA on "
        "change notice), Partner (external developers' code breaks when API "
        "changes; require 90-day deprecation notice, versioned endpoints "
        "maintained in parallel, per-API-key rate limiting). Explore what "
        "minimum set of controls the Partner BFF needs that internal BFFs "
        "don't require: semantic versioning, breaking-change policy, "
        "developer portal, and API key management."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** You have 3 BFFs (Mobile, Web, TV/Streaming). "
        "All 3 call the same 5 backend services. The operations team reports "
        "that a single backend service outage now simultaneously affects all 3 "
        "BFFs and all their users. Design a resilience strategy for BFFs that "
        "limits the blast radius of a single backend service outage."
    ),
    q3_hint=(
        "Think about what resilience options exist at the BFF layer: circuit "
        "breakers (stop calling the failing service, use cached or default "
        "data), partial response (return the page without the failing service's "
        "data rather than returning a full error), and priority degradation "
        "(serve critical data paths first during contention). Explore whether "
        "each BFF should implement its own resilience strategy independently "
        "based on what its client type can tolerate (mobile might accept cached "
        "data; web might show a visible error state for the failing section)."
    ),
)

upgrade(
    "MSV-028 - Service Mesh (Microservices).md",
    evo=(
        "Service meshes emerged as the operational complexity of managing "
        "resilience, observability, and security policies across many "
        "microservices became unsustainable at the application code level. "
        "Linkerd 1.0 (Twitter, 2016) was the first widely-adopted mesh. "
        "Istio (Google/IBM/Lyft, 2017) added mTLS, traffic management, and "
        "fine-grained authorization. Envoy (Lyft, 2016) became the universal "
        "data plane. The discipline evolved from 'implement resilience in each "
        "service' to 'delegate infrastructure concerns to a dedicated control "
        "plane' - separating policy definition (control plane) from policy "
        "enforcement (data plane)."
    ),
    tw_principle=(
        "Infrastructure concerns should be declarative and separate from "
        "application concerns. A service mesh applies the same principle as "
        "Kubernetes: declare the desired state (mTLS policy, circuit breaker "
        "threshold, traffic split), and let the infrastructure enforce it "
        "without application code changes. The separation between policy "
        "declaration and enforcement is the core value proposition."
    ),
    tw_bullets=(
        "- **Kubernetes Network Policies:** Declare which pods can communicate "
        "at the IP/port level, enforced by the CNI plugin - the same policy-"
        "as-declaration approach as a service mesh's AuthorizationPolicies, "
        "but at L3/L4 rather than L7.\n"
        "- **WAF rule sets:** A WAF declares which traffic patterns are allowed "
        "or blocked, applied to all traffic without modifying any application.\n"
        "- **Feature flags:** A feature flag system declares which users see "
        "which features, applied by the feature flag infrastructure without "
        "service code changes - declarative traffic management at the "
        "application feature level."
    ),
    st=(
        "Service meshes were sold as reducing operational complexity. In "
        "practice, they often increase it - especially during the first 6-12 "
        "months. Istio's control plane is itself a distributed system that can "
        "fail, causing mTLS outages for all services in the mesh. Envoy sidecar "
        "misconfiguration (a single bad VirtualService) can silently drop 100% "
        "of traffic for a service. Service mesh debugging requires understanding "
        "Envoy's xDS API, which is significantly more complex than reading an "
        "nginx config file. Teams that successfully adopt service meshes are "
        "those who invest in understanding Envoy's internal model before "
        "operating it in production - not those who install Istio and expect "
        "it to work without learning the underlying concepts."
    ),
    q1_hint=(
        "Think about what Istio adds to pod startup: the istio-init init "
        "container (iptables rules injection, 3-5 seconds), Envoy proxy startup "
        "and xDS configuration download from istiod (5-10 seconds), and "
        "sidecar injection (additional image pull). Explore which of these "
        "are configurable (startup probe timeouts, init container resource "
        "limits) and whether Istio's Ambient Mesh mode (no sidecars, per-node "
        "ztunnel) would eliminate the per-pod startup overhead entirely."
    ),
    q2_hint=(
        "Think about what OutlierDetection is actually measuring: 5xx responses "
        "from the payment service pods, not from the external payment gateway. "
        "When the gateway returns 503, the payment pods should distinguish "
        "between gateway-level errors (502/503 with specific body) and "
        "pod-level errors (500 Internal Server Error). Explore whether "
        "configuring OutlierDetection to only eject on `5xx` responses "
        "excluding 503 (a retriable error), and having the payment service "
        "return 503 when the gateway is down, would prevent pod ejection "
        "while the gateway is temporarily unavailable."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your team is evaluating Istio for a "
        "50-service Kubernetes cluster. Half the team supports it (mTLS, "
        "observability) and half opposes it (operational complexity, resource "
        "overhead). Design an adoption strategy that validates the benefits "
        "while limiting the risk during the adoption period."
    ),
    q3_hint=(
        "Think about incremental adoption: start with Istio in permissive mTLS "
        "mode (traffic encrypted opportunistically, but no enforcement) to "
        "validate observability benefits without security risk. Then enable "
        "strict mTLS for 3-5 non-critical services, then expand. Explore "
        "whether evaluating Ambient Mesh (no sidecars, lower resource overhead) "
        "provides a lower-barrier entry point, and what specific metrics "
        "(inter-service latency overhead, MTTR for incidents, security audit "
        "findings) would confirm the adoption is delivering value at each stage."
    ),
)

upgrade(
    "MSV-029 - Istio.md",
    evo=(
        "Istio was announced in 2017 as a joint project between Google, IBM, "
        "and Lyft, built on Envoy as its data plane. Version 1.0 (2018) marked "
        "production readiness. Early versions were criticised for extreme "
        "complexity (multiple control plane components: Pilot, Mixer, Citadel, "
        "Galley). Istio 1.6 (2020) merged these into a single istiod binary. "
        "Istio 1.22 (2024) introduced Ambient Mesh (sidecarless architecture) "
        "as the new default. The discipline evolved from 'install Istio and "
        "get all features for free' to 'adopt incrementally, understand the "
        "data plane, and choose the right mode for your workload.'"
    ),
    tw_principle=(
        "A control plane is more valuable than the specific policies it "
        "enforces. Istio's real value is not any individual feature (mTLS, "
        "circuit breaking, traffic splitting) - it is the ability to declare, "
        "version, and enforce these policies consistently across all services "
        "from a single control plane. The same principle governs Kubernetes "
        "(declare pod state), Terraform (declare infrastructure state), and "
        "GitOps (declare desired state in git, let the control plane converge)."
    ),
    tw_bullets=(
        "- **GitOps:** ArgoCD and Flux implement the same control plane pattern "
        "as Istio: declare desired state in git, continuously reconcile actual "
        "state with desired state.\n"
        "- **Kubernetes NetworkPolicy:** L3/L4 access control declared as "
        "Kubernetes resources, enforced by the CNI - control plane pattern "
        "at a different network layer.\n"
        "- **Database Row-Level Security:** PostgreSQL RLS declares which rows "
        "each user can access, enforced by the database engine - a control plane "
        "for data access."
    ),
    st=(
        "Istio's AuthorizationPolicy uses service account identities "
        "(SPIFFE/x509 certificates) for service-to-service authorization, not "
        "IP addresses or Kubernetes labels. This means that if two services "
        "share the same Kubernetes ServiceAccount, they are indistinguishable "
        "from Istio's AuthorizationPolicy perspective. Teams cannot write a "
        "policy that allows `order-service-v1` but not `order-service-v2` if "
        "both run under the same ServiceAccount. Correct Istio security design "
        "requires one ServiceAccount per microservice - a requirement "
        "Kubernetes itself does not enforce and that teams routinely violate "
        "for operational simplicity."
    ),
    q1_hint=(
        "Think about what 'emergency access' means in a zero-trust model: "
        "access should be time-limited, explicitly granted, automatically "
        "revoked, and audited. Explore whether a temporary AuthorizationPolicy "
        "with a short TTL (created via a GitOps commit to an emergency-access "
        "branch, automatically expired by a policy controller or TTL annotation), "
        "combined with Istio access log capture of the emergency session, "
        "provides the right balance between operational necessity and "
        "security auditability."
    ),
    q2_hint=(
        "Think about what Ambient Mesh changes architecturally: L4 processing "
        "moves to a per-node ztunnel DaemonSet (no per-pod sidecar), L7 "
        "processing moves to per-namespace or per-service waypoint proxies. "
        "VirtualService-based traffic management in sidecar mode is enforced "
        "by the Envoy sidecar on the caller side; in Ambient Mesh, it is "
        "enforced at the waypoint proxy. Explore whether your existing "
        "VirtualService canary deployment configs would work as-is in Ambient "
        "Mesh or require migration to waypoint proxy configuration."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Istio's mTLS adds 8ms latency per call to "
        "a performance-sensitive service. The security team requires mTLS for "
        "all inter-service communication. Design a technical resolution that "
        "satisfies the security requirement while minimising the latency impact."
    ),
    q3_hint=(
        "Think about what mTLS latency actually comes from: certificate "
        "handshake on new connections (one-time cost per connection, amortised "
        "over connection lifetime with keep-alive) vs TLS record "
        "encryption/decryption on each request (per-request, proportional to "
        "payload size). Explore whether HTTP/2 multiplexing + persistent "
        "connections (Envoy upstream_cx_reuse) reduces handshake amortisation "
        "overhead, and whether hardware-accelerated AES-NI instructions on "
        "modern CPUs reduce per-request encryption overhead below measurement "
        "threshold."
    ),
)

upgrade(
    "MSV-030 - Envoy Proxy.md",
    evo=(
        "Envoy Proxy was created at Lyft in 2015 and open-sourced in 2016 to "
        "address the failure modes of managing a microservices network without "
        "a unified proxy layer. Before Envoy, each service at Lyft had custom "
        "retry/timeout/circuit breaking logic in application code. The xDS "
        "(Discovery Service) API (formalised 2017) made Envoy dynamically "
        "configurable without restarts. Envoy became the universal data plane "
        "for Istio, Consul Connect, and AWS App Mesh - the single infrastructure "
        "component that all modern service meshes are built on."
    ),
    tw_principle=(
        "Infrastructure logic belongs in infrastructure, not application code. "
        "Envoy externalised retry, timeout, circuit breaking, observability, "
        "and TLS from every service into a single consistent proxy. When each "
        "service implements these independently, bugs in one service's "
        "resilience logic do not benefit other services. A centralised, "
        "consistently configured proxy is the correct place for cross-service "
        "infrastructure behaviour."
    ),
    tw_bullets=(
        "- **Kubernetes:** Kubernetes externalised container lifecycle management "
        "(previously Puppet/Ansible/init scripts), networking (CNI), and "
        "service discovery (previously Eureka in application code) - the same "
        "externalisation principle.\n"
        "- **Managed databases:** RDS externalised backup, replication, and "
        "failover from each team's custom database management scripts into "
        "managed infrastructure.\n"
        "- **CDN:** Content delivery networks externalised caching, geographic "
        "routing, and SSL termination from each application's custom code into "
        "managed infrastructure."
    ),
    st=(
        "Envoy's configuration API (xDS) is a distributed systems protocol "
        "more complex than most distributed systems it manages. A full Envoy "
        "configuration involves five separate gRPC streams (LDS, RDS, CDS, EDS, "
        "SDS), each with its own consistency model and failure mode. When Envoy "
        "is misconfigured (a common occurrence during control plane issues), "
        "traffic can be silently black-holed - all responses appear to succeed "
        "at the proxy level but no traffic reaches the upstream service. "
        "Debugging Envoy misconfiguration requires understanding xDS at a "
        "level of detail that most engineers take weeks to develop, making "
        "Envoy expertise one of the highest-value skills in modern platform "
        "engineering."
    ),
    q1_hint=(
        "Think about what happens when all endpoints are ejected: Envoy enters "
        "'panic mode' and routes to all endpoints regardless of ejection status "
        "to prevent total blackout. This is configurable via `panic_threshold`. "
        "Explore whether the correct configuration for a payment service with "
        "no fallback is to return 503 (circuit open) rather than routing to "
        "ejected endpoints in panic mode, and what the application should do "
        "when all Envoy endpoints are ejected (return a clear payment-"
        "unavailable response, not attempt a payment that will fail)."
    ),
    q2_hint=(
        "Think about what nginx capabilities need Envoy equivalents: complex "
        "rewrite rules (Envoy route matchers + header manipulation actions), "
        "SNI-based SSL (Envoy FilterChainMatch on `server_names`), Lua scripts "
        "(Envoy lua filter or ext_proc for external processing). Explore "
        "whether migrating endpoint-by-endpoint (one virtual host at a time, "
        "splitting traffic between nginx and Envoy at the load balancer level) "
        "is safer than an all-at-once cutover, and what the zero-downtime SDS "
        "certificate migration looks like (add to Envoy SDS while nginx still "
        "serves, shift DNS to Envoy, decommission nginx)."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A security CVE in Envoy requires upgrading "
        "all 500 Envoy sidecars in your cluster within 24 hours. Your current "
        "process (update Istio, roll all 500 deployments) takes 72 hours. "
        "Design a process that meets the 24-hour SLA for Envoy security "
        "upgrades."
    ),
    q3_hint=(
        "Think about what the 72-hour upgrade time is composed of: time to "
        "build a patched Istio release with the new Envoy (often hours after "
        "CVE disclosure), time to roll 500 deployments at your current rollout "
        "rate, and time to validate each service. Explore whether a dedicated "
        "Envoy image tag (independent of the Istio release cycle) allows "
        "security patches to be applied to Envoy without waiting for a full "
        "Istio release, and whether automated rolling with automated health "
        "checks can parallelise the validation step across all 500 services."
    ),
)

upgrade(
    "MSV-031 - Resilience4j.md",
    evo=(
        "Resilience4j emerged as the successor to Netflix Hystrix after Hystrix "
        "entered maintenance mode in 2018. Where Hystrix was thread-pool-based "
        "and JVM-blocking, Resilience4j was designed for functional programming "
        "and reactive streams, using decorator patterns to wrap any function. "
        "The library unified previously separate patterns (circuit breaker, "
        "retry, rate limiter, bulkhead, time limiter) into a single composable "
        "library. Spring Boot's @CircuitBreaker and @Retry annotations added "
        "framework-level adoption. The discipline evolved from 'implement "
        "resilience in application code' to 'apply resilience as a declarative "
        "aspect' via annotation-based configuration."
    ),
    tw_principle=(
        "Resilience patterns are cross-cutting concerns that should be composable "
        "and applied as decorators, not duplicated per-service or per-call. A "
        "circuit breaker wrapping a function is the same regardless of whether "
        "the function calls a database, an external API, or a message broker. "
        "The same principle governs all cross-cutting concern libraries: "
        "logging, metrics, and transaction management are applied via aspects, "
        "not manually coded in each business method."
    ),
    tw_bullets=(
        "- **Database connection pools:** HikariCP `maxPoolSize` is a bulkhead "
        "and `maxWait` is a timeout strategy applied to database access - "
        "Resilience4j's primitives implemented at the connection pool level.\n"
        "- **HTTP client configuration:** RestTemplate/OkHttp connection "
        "timeout is a timeout strategy; retry interceptors are retry patterns "
        "- Resilience4j's building blocks implemented in HTTP client libraries.\n"
        "- **Message consumer config:** Kafka `max.poll.interval.ms` is a "
        "timeout strategy; consumer group rebalancing on timeout is the fallback "
        "- resilience patterns in messaging middleware configuration."
    ),
    st=(
        "Resilience4j circuit breakers measure failure rates over a sliding "
        "window of calls - not over time. A service at 1,000 req/s completes "
        "the 10-call window in 10 milliseconds. A service at 1 req/s takes 10 "
        "seconds to complete the same window. This means circuit breakers "
        "configured by call count are extremely sensitive to traffic volume: "
        "low-traffic services take longer to detect failure patterns and longer "
        "to prove recovery. Teams routinely configure circuit breakers at "
        "development-time traffic levels that behave incorrectly in production "
        "- either too sensitive (opens on normal variance at high traffic) or "
        "too slow (takes minutes to detect real failures at low traffic)."
    ),
    q1_hint=(
        "Think about what a 10-call window means at 1000 req/s: the window "
        "completes every 10ms. At that rate, random request timing variations "
        "and thread scheduling jitter can produce apparent failure rates "
        "unrelated to the inventory service's actual health. Explore whether "
        "a time-based sliding window (measure failures over the last N seconds "
        "rather than N calls) is more stable at variable traffic volumes, and "
        "what minimum window duration provides the right sensitivity/stability "
        "tradeoff for a service that varies between 100 and 1000 req/s."
    ),
    q2_hint=(
        "Think about the interaction sequence: Resilience4j's CB fires first "
        "(it is in the application code, closer to the request). After "
        "Resilience4j opens, no calls go through to Istio (short-circuited at "
        "the application layer). Istio OutlierDetection never sees enough "
        "failing calls to open. Meanwhile, services without Resilience4j send "
        "calls through the Istio data plane, where OutlierDetection may "
        "eventually open. Explore whether this layered protection (app CB fires "
        "fast, mesh CB provides backstop for services without app-level CBs) "
        "is the correct design, or whether the two layers should be "
        "rationalised to avoid confusion about which layer is active."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Resilience4j retry is configured with "
        "`maxAttempts=3, waitDuration=500ms`. This is appropriate for "
        "idempotent GET calls but dangerous for non-idempotent POST calls "
        "(a retried POST might charge a customer twice). Design a retry "
        "configuration strategy that is safe for both without requiring "
        "engineers to manually check each usage site."
    ),
    q3_hint=(
        "Think about how to make the idempotent/non-idempotent distinction "
        "automatic: idempotent operations should have retry decorators; non-"
        "idempotent operations should not (or the destination service must "
        "support idempotency keys). Explore whether HTTP method awareness "
        "(retry GET/DELETE by default, never retry POST/PATCH unless "
        "`Idempotency-Key` header is present) or a custom `@IdempotentOperation` "
        "annotation can enforce the correct retry behaviour at the framework "
        "level rather than requiring per-call configuration."
    ),
)

upgrade(
    "MSV-032 - Circuit Breaker (Microservices).md",
    evo=(
        "The Circuit Breaker pattern was formalised by Michael Nygard in "
        "'Release It!' (2007) and popularised by Netflix Hystrix (2012), "
        "drawing from the analogy of electrical circuit breakers that interrupt "
        "current when it exceeds safe limits. Hystrix entering maintenance mode "
        "(2018) and Resilience4j becoming the standard Java implementation "
        "marked the pattern's maturation. The discipline evolved from "
        "'catch exceptions and return a fallback' to 'automatic failure "
        "detection with a three-state machine: Closed (normal), Open "
        "(failing, reject immediately), Half-Open (probing for recovery).'"
    ),
    tw_principle=(
        "The Circuit Breaker solves a fundamental distributed systems problem: "
        "a caller that keeps trying to call a failed service does worse than "
        "a caller that fails fast. Every retry to a failed service consumes "
        "resources (threads, connections, memory) that could serve other "
        "requests. The circuit breaker is a resource protection mechanism "
        "masquerading as a resilience feature."
    ),
    tw_bullets=(
        "- **TCP RST packet:** A TCP RST that immediately rejects a connection "
        "to a closed port is a circuit breaker in the network stack - fail fast "
        "rather than wait for a timeout.\n"
        "- **Kubernetes readiness probe:** A pod that fails its readiness check "
        "is removed from service endpoints - the platform-level circuit breaker "
        "for unhealthy instances.\n"
        "- **HTTP 429 Too Many Requests:** A rate-limiting response is the "
        "service's circuit breaker for a specific client - breaking the circuit "
        "of excessive requests before they consume capacity."
    ),
    st=(
        "The most dangerous circuit breaker misconfiguration is setting the "
        "timeout too long and the failure threshold too high together. A circuit "
        "breaker with a 10-second timeout and 50% failure threshold will not "
        "trip for a downstream service running at 600ms P99 (10x normal) with "
        "a 5% error rate. The service slowly drowns in slow calls that "
        "technically succeed - consuming 6x the thread capacity per request. "
        "Nygard calls this a 'cascading timeout failure': worse than a clean "
        "failure because the circuit breaker never opens and slow calls continue "
        "until the caller's thread pool is exhausted."
    ),
    q1_hint=(
        "Think about what 'critical service' means for fallback design: if the "
        "CB opens on Payments or Fraud Detection, the checkout must fail fast "
        "with a clear error (cannot complete a payment without the payment "
        "service). If the CB opens on Recommendations, the checkout should "
        "succeed without recommendations (return null or empty list). Explore "
        "whether Resilience4j's `fallback` method returning `null` for non-"
        "critical services (caller treats null as 'degraded, continue') vs "
        "re-throwing the exception for critical services (caller propagates "
        "as 503) cleanly separates the two cases."
    ),
    q2_hint=(
        "Think about what 10% failure rate across 20 independent circuit "
        "breakers means: each instance sees ~1 failure per 10-call window, "
        "well below the 50% threshold. No individual CB opens. Explore whether "
        "a centralised circuit breaker state (shared Redis counter, all 20 "
        "instances increment the same failure counter and read the same state) "
        "would aggregate failure signals to open when the aggregate rate "
        "exceeds the threshold, and what the operational complexity of "
        "centralised state is vs the protection gap of distributed state."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your circuit breaker has a 5-second timeout "
        "on inventory calls. During a traffic spike, the inventory service is "
        "slow (P99=4.8s) but healthy. The CB opens, causing healthy inventory "
        "calls to fail. How do you make timeout configuration adaptive to "
        "traffic patterns rather than fixed?"
    ),
    q3_hint=(
        "Think about what 'adaptive timeout' means: a timeout that adjusts "
        "based on currently observed latency rather than a configuration "
        "constant. Explore whether percentile-based timeouts (set timeout to "
        "2x the trailing P99 latency, computed over the last 60 seconds) or "
        "context-aware timeouts (longer during business hours when inventory "
        "is known to be slower) provide better protection than fixed timeouts, "
        "and what the minimum timeout floor should be to prevent the timeout "
        "from degrading faster than the real failure mode."
    ),
)

upgrade(
    "MSV-033 - Bulkhead Pattern.md",
    evo=(
        "The Bulkhead pattern was named after watertight compartments in ship "
        "hulls that prevent a single breach from sinking the entire vessel. "
        "Michael Nygard introduced it in 'Release It!' (2007) as the software "
        "equivalent: partition resources so that a failure in one partition "
        "cannot exhaust resources for other partitions. Netflix implemented it "
        "in Hystrix (2012) as the default resource isolation model. The "
        "discipline evolved from a theoretical fault isolation concept to a "
        "practical choice: thread-pool-based bulkheads (true OS thread "
        "isolation) vs semaphore-based bulkheads (concurrency limiting, "
        "lower overhead, preferred for reactive codebases)."
    ),
    tw_principle=(
        "Resource partitioning prevents correlated failures. When all service "
        "calls share a thread pool, a slow downstream fills all threads with "
        "waiting calls, starving faster services. Bulkheads partition the "
        "resource (thread pool, connection pool, memory) so each downstream "
        "has a dedicated allocation. The failure blast radius is bounded to "
        "the partition."
    ),
    tw_bullets=(
        "- **Database connection pools:** HikariCP configured with separate "
        "pool sizes for OLTP vs reporting is a bulkhead at the connection pool "
        "level - reporting queries cannot starve transactional queries.\n"
        "- **Kubernetes resource limits:** CPU and memory limits per pod are "
        "bulkheads at the process level - a memory leak in one pod cannot "
        "consume all node memory and starve other pods.\n"
        "- **Message queue partitioning:** Separate Kafka topics per priority "
        "(high-priority orders vs low-priority analytics) are bulkheads at the "
        "message bus level - low-priority processing cannot delay high-priority "
        "delivery."
    ),
    st=(
        "Netflix discovered that thread-pool-based bulkheads (Hystrix's default) "
        "have a surprisingly high overhead. With 40 services each having its "
        "own thread pool of 10 threads, the service has 400 OS threads just for "
        "isolation overhead - at 1MB of stack space each, that is 400MB of "
        "memory before the application does any work. Netflix documented this "
        "overhead as the primary motivation for semaphore-based bulkheads in "
        "reactive codebases. The trade-off: thread pools provide true resource "
        "isolation (one pool's blocked threads cannot affect another); "
        "semaphores only limit concurrency (no thread isolation, but also no "
        "thread creation overhead per isolated service)."
    ),
    q1_hint=(
        "Think about Little's Law: L = lambda * W, where L is average concurrent "
        "requests, lambda is arrival rate, W is average service time. For "
        "Payments: L = 500 * 0.05 = 25 concurrent; for Inventory: L = 500 * "
        "0.2 = 100 concurrent. These are the minimum bulkhead sizes. Explore "
        "what safety margin above the minimum is appropriate (2x is a common "
        "starting point) and what the total thread count is when you sum all "
        "four bulkheads, plus a margin for the main application thread pool."
    ),
    q2_hint=(
        "Think about what a Semaphore Bulkhead protects in reactive code: not "
        "OS threads (WebFlux/Project Reactor does not block them) but event "
        "loop capacity - 20 concurrent reactive subscriptions to a 2000ms "
        "service each hold a reactive chain in memory and consume event loop "
        "scheduler slots. Explore whether 20 concurrent subscriptions to a "
        "2000ms service at 1000 req/s means 2000 in-flight chains without "
        "limiting (2000 * 2s window = 2000 concurrent), making 20 far too "
        "restrictive for a reactive system."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A single Bulkhead protects all calls to a "
        "payment gateway that has two endpoints: `/authorize` (called on every "
        "checkout, P50=100ms) and `/refund` (rare, P50=2000ms). A wave of "
        "refunds fills the shared Bulkhead, rejecting authorization requests "
        "and blocking customer checkouts. Redesign the Bulkhead strategy."
    ),
    q3_hint=(
        "Think about whether a single Bulkhead for both endpoints is the right "
        "granularity: refunds and authorizations have different SLAs, different "
        "volumes, and dramatically different latency profiles. Explore whether "
        "separate Bulkheads for `/authorize` and `/refund` (sized by Little's "
        "Law for each endpoint's traffic independently) with different priority "
        "queuing (authorization requests preempt refund requests during "
        "contention) would prevent refunds from starving authorizations."
    ),
)

upgrade(
    "MSV-034 - Rate Limiting (Microservices).md",
    evo=(
        "Rate limiting evolved from connection throttling (network layer, 1990s) "
        "to application-level HTTP API throttling. Token Bucket and Leaky Bucket "
        "algorithms (network engineering, 1980s) were adapted for HTTP APIs. "
        "GitHub popularised per-client rate limits with standard headers "
        "(X-RateLimit-Remaining, Retry-After) in 2011. AWS API Gateway's "
        "built-in rate limiting (2015) made it a managed service pattern. "
        "The discipline evolved from 'protect your servers from abuse' to "
        "'implement fair multi-tenant resource sharing': per-client-tier limits, "
        "per-endpoint limits, and distributed rate limiting across instances."
    ),
    tw_principle=(
        "Rate limiting is fair resource allocation, not just abuse prevention. "
        "A rate limit tells each client: 'This is your guaranteed share of "
        "capacity.' Without rate limits, a single large client can consume all "
        "available capacity, starving other clients. The same principle governs "
        "CPU scheduling (time slicing ensures no process monopolises the CPU), "
        "database connection pools (max connections per user), and network QoS "
        "(traffic shaping for bandwidth fairness)."
    ),
    tw_bullets=(
        "- **Database query throttling:** Limiting concurrent queries per "
        "session is rate limiting at the database level - protecting shared "
        "resources from individual query storms.\n"
        "- **Email sending:** Email providers (SendGrid, Mailgun) rate limit "
        "per API key to protect deliverability reputation - rate limiting "
        "applied to communication channels.\n"
        "- **CI/CD build systems:** GitHub Actions minutes and Jenkins "
        "concurrent build limits are rate limiting applied to compute resource "
        "allocation per account."
    ),
    st=(
        "The most counterintuitive property of rate limiting is that it can "
        "make systems less reliable when misconfigured. A rate limit set below "
        "legitimate peak demand rejects valid requests during high-traffic "
        "events (product launches, viral posts). The most common failure is "
        "setting limits based on average traffic rather than peak demand: a "
        "system handling 100 req/s average but 500 req/s peak needs a rate "
        "limit of 500, not 100. Teams that set limits based on average traffic "
        "reject 80% of legitimate peak requests and provide no protection value "
        "to their users - the worst of both worlds."
    ),
    q1_hint=(
        "Think about what fixed-window means: the counter resets at each second "
        "boundary. A client who knows the exact reset time sends N requests "
        "just before the reset and N more just after, achieving 2N requests in "
        "a very short window while both windows show N (within limit). Explore "
        "how a sliding window (count requests in the last N seconds "
        "continuously, not since the last reset) eliminates this boundary "
        "exploit, and what the implementation cost difference is between a "
        "Redis atomic counter (fixed window) and a Redis sorted set with "
        "timestamps (sliding window)."
    ),
    q2_hint=(
        "Think about what per-instance rate limiting means: each instance has "
        "its own independent counter, with no coordination. A client distributing "
        "10 req/s to each of 10 instances sends 100 req/s total but never "
        "exceeds any single instance's 100 req/s limit. Explore whether a "
        "centralised rate limiter (Redis INCR shared across all instances, "
        "checked on each request) solves this, and what the latency cost of "
        "a Redis round-trip is on every rate limit check (typically 1-2ms, "
        "multiplied by all requests)."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** A DDoS attack uses 10,000 unique bot IPs, "
        "each sending exactly 99 req/s (1 below your per-IP limit of 100). "
        "Collectively they generate 990,000 req/s. No individual IP hits the "
        "rate limit. Your service is overwhelmed. Design additional protection "
        "layers that handle this scenario."
    ),
    q3_hint=(
        "Think about what per-IP rate limiting cannot defend against: a "
        "distributed attack where each attacker stays below the per-IP limit. "
        "Explore whether aggregate rate limiting (total requests across all "
        "clients caps total service throughput), IP reputation filtering "
        "(blocking known bad IPs via threat intelligence), bot detection "
        "(browser fingerprinting, CAPTCHA on suspicious traffic), and geographic "
        "rate limiting (block entire ASNs under active attack) provide defense-"
        "in-depth. Note these are WAF/CDN layer controls, not just application-"
        "level rate limiting."
    ),
)

upgrade(
    "MSV-035 - Timeout Strategy.md",
    evo=(
        "Timeout strategies evolved from simple socket-level timeouts (TCP "
        "send/receive, 1980s) to application-level cascading deadline "
        "propagation. Early distributed systems had no timeout concepts - "
        "a call to a hung remote service would wait forever. Michael Nygard's "
        "'Release It!' (2007) documented timeout as the most important "
        "reliability pattern. Google's internal Deadline Propagation concept "
        "(making every inter-service call carry a remaining deadline) became "
        "an external standard as gRPC's deadline propagation feature (2016). "
        "The discipline evolved from 'set a timeout on every call' to "
        "'propagate decreasing deadlines through the entire call chain.'"
    ),
    tw_principle=(
        "Every distributed system call needs a timeout, and the downstream "
        "timeout must be shorter than the caller's timeout. This is deadline "
        "propagation: if Service A has 200ms to respond to the user, it should "
        "set no more than 150ms timeout on Service B, which should set no more "
        "than 100ms on Service C. At each layer, the timeout is the remaining "
        "deadline minus processing overhead - never a fixed value chosen "
        "independently of the full call chain."
    ),
    tw_bullets=(
        "- **HTTP client configuration:** Connection timeout (how long to wait "
        "for TCP handshake) and read timeout (how long to wait for response) "
        "are deadline propagation at the network call level.\n"
        "- **Database query timeouts:** PostgreSQL `statement_timeout` ensures "
        "slow queries don't hold locks indefinitely and don't consume query "
        "slots beyond the application's latency budget.\n"
        "- **Job schedulers:** Maximum execution time per job ensures hung jobs "
        "don't prevent other jobs from running - deadline propagation applied "
        "to batch processing."
    ),
    st=(
        "The most counterintuitive finding about timeout strategies is that "
        "shorter timeouts don't always improve reliability. A timeout that is "
        "too short creates a 'timeout storm': callers time out before the "
        "downstream service can respond, the downstream finishes processing and "
        "sends a response to nobody, and callers immediately retry - creating "
        "higher downstream load than without any callers retrying. At scale, "
        "timeout storms can cause the downstream service to experience more "
        "load than it would under normal conditions. The optimal timeout is the "
        "minimum value above which the response is too late to be useful - not "
        "the minimum the network can achieve."
    ),
    q1_hint=(
        "Think about what B's 300ms timeout and A's 200ms timeout means: if C "
        "takes 250ms, C responds within B's budget, B tries to respond to A - "
        "but A may have already timed out after 200ms (the time B waited for C "
        "alone, without B's processing time). B's 300ms timeout is useless when "
        "A only waits 200ms total. Now trace with B's timeout reconfigured to "
        "150ms: C takes 250ms, exceeding B's 150ms timeout; B times out "
        "and returns an error to A within A's 200ms budget. A receives an error "
        "response instead of a timeout - which is better (faster failure)."
    ),
    q2_hint=(
        "Think about what P50=40ms but 2% timeouts means statistically: 2% of "
        "requests have latency >500ms. Check whether the distribution is "
        "bimodal (fast path: 40ms, slow path: 600ms) indicating a specific "
        "code path or resource contention. Diagnostic steps: (1) check "
        "inventory service P95/P99 from its own metrics (not caller's view); "
        "(2) check if the 2% correlates with specific operations or specific "
        "inventory items; (3) check GC pause logs on the inventory service; "
        "(4) check network packet loss between services (mtr/traceroute)."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your service calls 3 dependencies "
        "sequentially: Cache (timeout=50ms), Database (timeout=200ms), and "
        "External Payment API (timeout=3000ms). Your SLA to the user is 5 "
        "seconds. Design the timeout configuration and communication pattern "
        "that maximises successful responses within the SLA even when "
        "individual dependencies are slow."
    ),
    q3_hint=(
        "Think about whether the 3 calls must be sequential or can be "
        "parallelised: if Cache and Database don't depend on each other's "
        "output, calling them in parallel reduces total latency to "
        "max(50ms, 200ms)=200ms instead of 250ms. Explore whether the External "
        "Payment API call can be made asynchronously (submit payment, receive "
        "webhook or poll for result) to avoid holding the user's request for "
        "up to 3 seconds, and what timeout budget remains for each operation "
        "after parallelisation reduces the sequential component."
    ),
)

print("\nBatch 3 (MSV-026 to MSV-035) complete.")
