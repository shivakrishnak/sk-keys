param()
Set-Location "c:\ASK\MyWorkspace\sk-keys"
$d = "c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SYD-system-design"

$gem   = [char]::ConvertFromUtf32(0x1F48E)
$bulb  = [char]::ConvertFromUtf32(0x1F4A1)
$brain = [char]::ConvertFromUtf32(0x1F9E0)
$link  = [char]::ConvertFromUtf32(0x1F517)
$star  = [char]0x2605
$empty = [char]0x2606

function Join-Lines { param([string[]]$lines) return $lines -join "`r`n" }

function Upgrade-SYD {
    param(
        [string]$filename,
        [string]$newYaml,
        [string]$inventionMomentQuote,
        [string]$evolutionText,
        [string]$newRelatedContent,
        [string]$twContent,
        [string]$stContent,
        [string]$newThinkContent
    )
    $fp = "$d\$filename"
    $c = [System.IO.File]::ReadAllText($fp, [System.Text.Encoding]::UTF8)
    $nl = if ($c.Contains("`r`n")) { "`r`n" } else { "`n" }

    $fmEnd = $c.IndexOf("---", 4)
    $afterFm = $c.Substring($fmEnd + 3)
    $c = $newYaml + $afterFm

    if ($c.Contains($inventionMomentQuote)) {
        $c = $c.Replace($inventionMomentQuote, $inventionMomentQuote + $nl + $nl + "**EVOLUTION:**" + $nl + $evolutionText)
    } else { Write-Warning "Invention moment not found in $filename" }

    $rkHeader = "### $link Related Keywords"
    $rkPos = $c.IndexOf($rkHeader)
    if ($rkPos -ge 0) {
        $afterRk = $c.IndexOf("---", $rkPos + $rkHeader.Length)
        $newRk = $rkHeader + $nl + $nl + $newRelatedContent + $nl + $nl
        $c = $c.Substring(0, $rkPos) + $newRk + $c.Substring($afterRk)
    } else { Write-Warning "Related Keywords not found in $filename" }

    $thinkHeader = "### $brain Think About This Before We Continue"
    $thinkPos = $c.IndexOf($thinkHeader)
    if ($thinkPos -ge 0) {
        $dashBefore = $c.LastIndexOf($nl + "---" + $nl, $thinkPos)
        $bodyPart = $c.Substring(0, $dashBefore)
        $newTail = $nl + "---" + $nl + $nl +
            "### $gem Transferable Wisdom" + $nl + $nl + $twContent + $nl + $nl +
            "---" + $nl + $nl +
            "### $bulb The Surprising Truth" + $nl + $nl + $stContent + $nl + $nl +
            "---" + $nl + $nl +
            $thinkHeader + $nl + $nl + $newThinkContent + $nl
        $c = $bodyPart + $newTail
    } else { Write-Warning "Think section not found in $filename" }

    $c = $c.Replace("_Hint:_", "*Hint:*")
    [System.IO.File]::WriteAllText($fp, $c, [System.Text.Encoding]::UTF8)
    Write-Host "OK: $filename" -ForegroundColor Green
}

# ============================================================
# SYD-011 - Consistent Hashing (Load Balancing)
# ============================================================
$yaml011 = Join-Lines @(
    "---",
    "id: SYD-011",
    "title: `"Consistent Hashing (Load Balancing)`"",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: $star$star$star",
    "depends_on: SYD-008, SYD-009",
    "used_by: SYD-031",
    "related: SYD-031, SYD-009, SYD-008",
    "tags:",
    "  - algorithm",
    "  - deep-dive",
    "  - distributed",
    "  - advanced",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 11",
    "permalink: /syd/consistent-hashing/",
    "---"
)

$inv011 = '"This is why consistent hashing was invented-add servers without reshuffling most data."'

$evo011 = "Consistent hashing was invented by Karger et al. in 1997 to solve CDN cache invalidation at internet scale - when a cache server is added or removed, only 1/N of keys should move, not all of them. Amazon's Dynamo (2007) brought consistent hashing to production databases, making it a foundational distributed systems pattern. Modern implementations add token-based partitioning (Cassandra), bounded load (Google), and virtual node counts tuned to the expected cluster size. Today, consistent hashing is the default partitioning strategy for distributed caches, databases, and service mesh load balancers."

$rk011 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-008 - Load Balancing]] - the distribution problem this solves",
    "- [[SYD-009 - Round Robin]] - the simpler algorithm to compare against",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-031 - Sharding (System)]] - uses consistent hashing to partition data across nodes",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-009 - Round Robin]] - simpler, no affinity, correct for stateless workloads",
    "- [[SYD-010 - Least Connections]] - adaptive but no cache/session affinity"
)

$tw011 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "Minimise the amount of work required to rebalance when the cluster changes. This principle appears in every partitioning system: database sharding adds extra partitions for flexibility, Kafka over-partitions topics to allow consumer rebalancing, and virtual nodes in consistent hashing absorb failures without full rehashing. The invariant: design for change with minimal disruption.",
    "",
    "**Where else this pattern appears:**",
    "- **Cassandra token ring:** Each node owns a range of tokens on a consistent hash ring - adding a node splits existing ranges rather than redistributing all data.",
    "- **Redis Cluster:** Uses a 16,384-slot consistent hashing variant where slots are assigned to nodes and migrate incrementally when nodes are added.",
    "- **CDN edge routing:** Consistent hashing routes requests for the same URL to the same edge server - maximising cache hit rate across the fleet."
)

$st011 = "The original consistent hashing paper by Karger et al. was written specifically to solve the CDN cache problem: when a web cache server is added or removed, how do you avoid invalidating all cached content? The ring abstraction solved a CDN problem but became the foundation of every major distributed database. Cassandra, Riak, Amazon DynamoDB, and CockroachDB all use consistent hashing variants - not because of load balancing but because of the CDN insight about minimising key movement during cluster topology changes."

$think011 = Join-Lines @(
    "**Q1.** With consistent hashing, adding one server rehashes ~1/N keys. With N=1000 servers and 1 billion keys, that is 1 million migrations. They happen in the background. But what if a client queries a key that hasn't migrated yet - it's still on the old server? How does the system handle this during the migration window?",
    "",
    "*Hint:* Think about what migrated means from the client's perspective - does the client know which server owns a key, and how quickly does migration happen? Explore whether the migration is atomic (all-at-once switch) or gradual (background copy with dual reads).",
    "",
    "**Q2.** A server crashes. Keys map to next server clockwise (automatic failover). But if you add a replacement server at the same position on the ring, old keys migrate back. What happens to data on the new server - is it overwritten? How do you handle keys on two servers temporarily?",
    "",
    "*Hint:* Think about what happens to data on the replacement server when old keys migrate back - do clients write to the new server before, during, or after the migration? Explore how distributed databases handle this with read repair or hinted handoff.",
    "",
    "**Q3 (Root Cause):** A consistent hashing ring has 10 servers. Server 5 is removed. Server 6 now owns all of Server 5's keys. Server 6's load triples and it starts to slow down. How does this hotspot form, and what prevents it in production systems?",
    "",
    "*Hint:* Think about how many virtual nodes each server has and whether virtual node distribution was uniform across the ring. Explore how bounded load extensions to consistent hashing cap the maximum load ratio on any single server."
)

Upgrade-SYD "SYD-011 - Consistent Hashing (Load Balancing).md" $yaml011 $inv011 $evo011 $rk011 $tw011 $st011 $think011

# ============================================================
# SYD-012 - Sticky Sessions
# ============================================================
$yaml012 = Join-Lines @(
    "---",
    "id: SYD-012",
    "title: Sticky Sessions",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: $star$star$empty",
    "depends_on: SYD-008",
    "used_by: SYD-013",
    "related: SYD-013, SYD-008, SYD-007",
    "tags:",
    "  - intermediate",
    "  - architecture",
    "  - pattern",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 12",
    "permalink: /syd/sticky-sessions/",
    "---"
)

$inv012 = '"This is why sticky sessions were created-pin each user to one server so their session data stays local."'

$evo012 = "Sticky sessions were the standard solution for stateful web applications in the early 2000s - before centralised session stores were viable at scale. As Redis and Memcached became available as managed cloud services, distributed session storage replaced stickiness for new applications. Modern architectures default to stateless design (JWT tokens, externalised session state) - but sticky sessions remain the practical fallback for legacy monoliths, stateful WebSocket connections, and applications where session migration is prohibitively expensive to implement."

$rk012 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-008 - Load Balancing]] - the context where stickiness is configured",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-013 - Session Affinity]] - related concept; affinity is the mechanism, stickiness is the policy",
    "- [[SYD-007 - Horizontal Scaling]] - horizontal scaling works best when stickiness is eliminated",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-013 - Session Affinity]] - often used synonymously; affinity is more general",
    "- [[SYD-007 - Horizontal Scaling]] - true horizontal scalability requires stateless design, not stickiness"
)

$tw012 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "State that is local to one node is a scaling barrier. When local state is unavoidable (legacy monolith, expensive migration), route consistently to the same node for the same client. This principle appears in database sharding (shard by user ID for user data locality), Kafka partition assignment (topic partition sticky to consumer), and CPU cache affinity (pin threads to cores to preserve L1/L2 cache warmth).",
    "",
    "**Where else this pattern appears:**",
    "- **Database connection pools:** A transaction must use the same connection throughout (connection affinity) because transactions are stateful on the database server side.",
    "- **Kafka consumer groups:** Each partition is assigned to exactly one consumer - a form of sticky partitioning to avoid rebalancing overhead.",
    "- **gRPC load balancing:** gRPC connections carry stream state; sticky routing to the same backend server preserves stream context across requests."
)

$st012 = "Sticky sessions can make load balancing counterproductive. If 10% of your users are heavy users (high-traffic tenants, enterprise customers), and they all happen to hash to the same server via IP-based stickiness, that server receives 10x the load of others. This is the hot user problem: server load is not determined by number of users but by user activity distribution. Organisations that deploy sticky sessions without monitoring per-server request rates routinely see 3-4x load imbalance that appears invisible in aggregate cluster-level metrics."

$think012 = Join-Lines @(
    "**Q1.** A user logs in from home (IP = 203.0.113.5, pinned to Server 1). They switch to mobile (new IP = 198.51.100.1). Load balancer sees new IP, pins them to Server 2. But their session is on Server 1. What happens when they try to fetch their user profile - is session lost, or can Server 2 find it?",
    "",
    "*Hint:* Think about what happens at Layer 7: when the load balancer sees a new IP it routes to Server 2, but the session cookie (or app-level session ID) still references data stored on Server 1. Explore whether session data is stored in application memory, a database, or a cookie - only one of these allows Server 2 to retrieve it.",
    "",
    "**Q2.** You're using sticky sessions with IP-based stickiness. A corporate proxy/NAT sits in front - 100 employees go through the same proxy IP. The LB sees them all as the same client (same IP), pins all 100 to Server 1. Server 1 becomes 100x overloaded. How can this disaster be prevented?",
    "",
    "*Hint:* Think about what the load balancer uses as the sticky key when all 100 employees share the same IP. Explore whether cookie-based stickiness (SESSIONID cookie) would solve the NAT problem and what happens when a corporate proxy strips cookies.",
    "",
    "**Q3 (System Interaction):** You have sticky sessions based on SESSIONID cookie. A user's session is 2 MB of in-memory state on Server 1. Server 1 dies. The user's next request goes to Server 2. Design a session recovery strategy that minimises data loss without requiring a full login cycle.",
    "",
    "*Hint:* Think about whether session data can be persisted to a shared store asynchronously (session replication) vs on-demand (user gets a degraded session and re-authenticates specific parts), and what the trade-off is between synchronous replication overhead and recovery completeness."
)

Upgrade-SYD "SYD-012 - Sticky Sessions.md" $yaml012 $inv012 $evo012 $rk012 $tw012 $st012 $think012

# ============================================================
# SYD-013 - Session Affinity
# ============================================================
$yaml013 = Join-Lines @(
    "---",
    "id: SYD-013",
    "title: Session Affinity",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: $star$star$empty",
    "depends_on: SYD-008, SYD-012",
    "used_by:",
    "related: SYD-012, SYD-008",
    "tags:",
    "  - intermediate",
    "  - architecture",
    "  - pattern",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 13",
    "permalink: /syd/session-affinity/",
    "---"
)

$inv013 = '"This is why session affinity was created-guarantee that a user''s related requests stay together on one server, preserving session coherency."'

$evo013 = "Session affinity and sticky sessions emerged simultaneously as solutions to the stateful web server problem. The distinction between affinity (software-level routing preference) and stickiness (hard pinning) emerged as load balancers became more sophisticated. Modern service meshes (Envoy, Istio) implement session affinity as a first-class routing policy with configurable hash keys and fallback behaviour. The trend toward JWT and cookie-based client state has reduced the need for server-side affinity - but it remains essential for WebSocket connections, gRPC streaming, and database connection poolers."

$rk013 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-008 - Load Balancing]] - the infrastructure implementing affinity",
    "- [[SYD-012 - Sticky Sessions]] - the related concept; stickiness is the common implementation",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-007 - Horizontal Scaling]] - affinity-free design is required for true horizontal scalability",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-012 - Sticky Sessions]] - often used synonymously; stickiness is a specific type of affinity",
    "- [[SYD-007 - Horizontal Scaling]] - scales better when affinity is eliminated through stateless design"
)

$tw013 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "When state is local to a worker, route consistently to the same worker. This appears in database connection pooling (route the same transaction to the same connection), CPU cache affinity (pin the same thread to the same core), and Kafka partition assignment (same consumer group member owns the same partition). The invariant: local state requires routing consistency.",
    "",
    "**Where else this pattern appears:**",
    "- **Database transactions:** A transaction must use the same database connection throughout - connection affinity ensures ACID properties are maintained by a single session.",
    "- **Kubernetes StatefulSets:** Pods in a StatefulSet have stable network identifiers - clients can route to pod-0, pod-1 consistently for stateful applications like databases.",
    "- **WebSocket upgrades:** Once a WebSocket is established to a server, all subsequent frames go to that server - affinity at the protocol level, not the load balancer."
)

$st013 = "Session affinity creates a silent scalability cliff. As long as a server runs normally, affinity works perfectly. But when that server receives uneven load (one user is heavy, or one IP maps to many users behind NAT), the affinity causes runaway load concentration that is invisible in per-application aggregate metrics. Engineers debugging mysterious performance degradation on one server often discover that affinity - correctly routing a heavy user to the same server every time - is the cause. The fix (switch to distributed session) is straightforward in greenfield but extremely expensive in legacy applications with years of state-on-heap assumptions."

$think013 = Join-Lines @(
    "**Q1.** Session affinity uses a session cookie as the affinity key. But the cookie is created on the server that handles the first request. What happens if the user's first request to a load balancer coincides with that server being overloaded - should the LB override affinity and send to a less-loaded server, risking session fragmentation?",
    "",
    "*Hint:* Think about what overloaded means in the context of affinity - the first request establishes the affinity, so the server is chosen before its load is known. Explore whether dynamic affinity (change servers on overload) breaks session coherency and what that trade-off costs the user experience.",
    "",
    "**Q2.** A distributed system needs session affinity (routing) AND session durability (persistence). Affinity alone doesn't replicate data. How would you combine affinity with session replication to achieve both? What's the overhead?",
    "",
    "*Hint:* Think about what session replication requires: all writes on Server A must be propagated to Server B before Server B can serve a request for that session. Explore the synchronous vs asynchronous replication trade-off and how sticky sessions become a fallback when replication lag is too high.",
    "",
    "**Q3 (Design Trade-off):** You're designing a real-time collaborative document editor. Multiple users editing the same document need to connect to the same server to receive updates. Design a routing strategy that balances load while keeping collaborators on the same server.",
    "",
    "*Hint:* Think about what the affinity key should be (user ID, document ID, or session ID) and whether it's the user or the document that determines server assignment. Explore how WebSocket upgrade requests carry the document ID and how the load balancer can use it for routing."
)

Upgrade-SYD "SYD-013 - Session Affinity.md" $yaml013 $inv013 $evo013 $rk013 $tw013 $st013 $think013

# ============================================================
# SYD-014 - Auto Scaling
# ============================================================
$yaml014 = Join-Lines @(
    "---",
    "id: SYD-014",
    "title: Auto Scaling",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: $star$star$empty",
    "depends_on: SYD-007, SYD-008, SYD-027",
    "used_by:",
    "related: SYD-027, SYD-008, SYD-007",
    "tags:",
    "  - cloud",
    "  - performance",
    "  - intermediate",
    "  - architecture",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 14",
    "permalink: /syd/auto-scaling/",
    "---"
)

$inv014 = '"This is why auto-scaling was invented-automatically add servers when load spikes, remove them when traffic drops."'

$evo014 = "Auto-scaling began as a proprietary cloud feature - AWS Auto Scaling launched in 2009, the first managed service to automatically provision and terminate EC2 instances based on CloudWatch metrics. The concept was quickly adopted across all cloud providers. Kubernetes Horizontal Pod Autoscaler (2016) brought auto-scaling to containerised workloads. Modern implementations added predictive scaling (ML-based pre-warming before traffic arrives), scale-to-zero (serverless), and per-metric scaling (scale on queue depth, latency percentiles, or custom business metrics). The discipline evolved from reactive capacity management to proactive traffic shaping."

$rk014 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-007 - Horizontal Scaling]] - the underlying technique that auto-scaling automates",
    "- [[SYD-008 - Load Balancing]] - required to distribute traffic to new instances",
    "- [[SYD-027 - Capacity Planning]] - forecasting to set auto-scaling parameters correctly",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-025 - Thundering Herd]] - failure mode that auto-scaling can trigger or amplify",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-006 - Vertical Scaling]] - manual alternative; scale up one machine instead of out",
    "- [[SYD-027 - Capacity Planning]] - complementary: forecasting replaces reactive scaling for predictable load"
)

$tw014 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "A system that self-adjusts based on observed load applies feedback control - the same principle as a thermostat, PID controller, or TCP congestion control. The key design question is always: what is the lag between measurement and adjustment? In auto-scaling, instance launch time is the lag; in TCP, round-trip time is the lag; in thermostats, thermal mass is the lag. Minimising or compensating for lag determines the quality of the control loop.",
    "",
    "**Where else this pattern appears:**",
    "- **TCP congestion control:** AIMD (additive increase, multiplicative decrease) adjusts send rate based on packet loss signals - a feedback loop with network RTT as lag.",
    "- **Database connection pools:** Pool size adjusts based on connection wait time - auto-scaling at the connection management layer.",
    "- **Cache warming:** Predictive cache pre-loading based on traffic patterns is proactive auto-scaling for cache capacity."
)

$st014 = "Auto-scaling can amplify failure cascades. When a dependency becomes slow (database latency spikes), requests queue up, CPU stays high (requests are running, not completing), and auto-scaling adds more instances. More instances means more concurrent requests to the already-slow database, making the database slower. This is the thundering herd auto-scaler failure mode: auto-scaling responds correctly to CPU signals but amplifies the root cause. Production systems add circuit breakers and rate limits specifically to prevent auto-scaling from making database failures worse."

$think014 = Join-Lines @(
    "**Q1.** Auto-scaling launches new instances based on CPU > 70%. But what if the spike is transient (1-second spike, then drops)? New instances take 2 minutes to launch. By the time they're ready, traffic has passed. Worse, now you have excess capacity that triggers scale-down. How do you avoid this wasted provisioning?",
    "",
    "*Hint:* Think about what happens to the scaling decision lag when the spike is shorter than the instance launch time. Explore whether pre-warming (launching instances before the spike) or caching (reducing per-request backend load) addresses the problem better than faster launch times.",
    "",
    "**Q2.** An instance is marked for termination (graceful shutdown). It drains existing connections but takes 5 minutes. During those 5 minutes, other instances become overloaded. Their CPU spikes, triggering scale-up. New instances launch. But the terminating instance finally completes, and scale-down triggers again. How do you coordinate these events to prevent thrashing?",
    "",
    "*Hint:* Think about what 5 minutes to drain means for the total pool size during that period - the pool effectively shrinks by 1. Explore whether setting a minimum cool-down period between scale-down events prevents the chain reaction.",
    "",
    "**Q3 (Scale):** Your auto-scaler triggers on CPU > 70%. A bug in a new deployment causes infinite loops in 5% of requests - those requests never complete, so CPU stays high. Auto-scaling keeps adding instances. The bug is not caught for 30 minutes. Design safeguards to prevent runaway scaling in this scenario.",
    "",
    "*Hint:* Think about what metrics auto-scaling cannot distinguish (CPU from bad requests looks the same as CPU from good requests) and what signals would catch the infinite loop (error rate, P99 latency, memory growth per request). Explore whether a maximum scaling ceiling or a canary deployment strategy would have contained the blast radius."
)

Upgrade-SYD "SYD-014 - Auto Scaling.md" $yaml014 $inv014 $evo014 $rk014 $tw014 $st014 $think014

# ============================================================
# SYD-015 - SLA SLO SLI
# ============================================================
$yaml015 = Join-Lines @(
    "---",
    "id: SYD-015",
    "title: SLA SLO SLI",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: $star$star$empty",
    "depends_on:",
    "used_by: SYD-016, SYD-017",
    "related: SYD-016, SYD-017",
    "tags:",
    "  - reliability",
    "  - intermediate",
    "  - architecture",
    "  - observability",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 15",
    "permalink: /syd/sla-slo-sli/",
    "---"
)

$inv015 = '"This is why SLA/SLO/SLI were created-define what ''reliable'' means, commit to targets, and measure reality."'

$evo015 = "SLA as a legal contract predates software engineering - telecommunications companies used SLAs in the 1970s to define service quality commitments. The Google SRE book (2016) transformed SLAs from legal boilerplate into engineering tools: SLOs gave teams internal targets to aim for, SLIs gave them metrics to measure against, and error budgets gave them permission to ship. The framework spread beyond Google to become the standard reliability discipline across the industry. Modern implementations extend the concept to synthetic monitoring (measuring SLIs from the user's perspective), multi-tier SLAs, and SLOs as code (SLO configuration in version control)."

$rk015 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-014 - Auto Scaling]] - infrastructure decisions affect achievable SLO",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-016 - Error Budget]] - derived directly from SLO",
    "- [[SYD-017 - MTTR MTBF]] - complementary operational metrics that affect SLA achievement",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-016 - Error Budget]] - error budget is the operational tool derived from SLA/SLO",
    "- [[SYD-017 - MTTR MTBF]] - different but complementary reliability metrics"
)

$tw015 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "Making a commitment explicit forces alignment. An SLA is a commitment to a customer. An SLO is a commitment within the team. The principle - define the target explicitly before measuring - applies everywhere: capacity planning (define threshold before monitoring), performance tuning (define acceptable latency before optimising), and hiring (define success criteria before interviewing). Ambiguous targets produce ambiguous outcomes.",
    "",
    "**Where else this pattern appears:**",
    "- **Capacity planning:** A capacity threshold (CPU < 70%) is an internal SLO for infrastructure - you monitor against it and provision to maintain it.",
    "- **Test coverage targets:** A team's 80% coverage target is an SLO for code quality - it creates shared accountability without being a customer-facing commitment.",
    "- **Delivery SLAs:** A product team's commitment to deliver a feature by Q3 is an SLA - with the same structure of measurement, target, and consequence."
)

$st015 = "Google's original SRE insight - that 100% availability is the wrong target - was counterintuitive when published. The argument: if your SLA is 99.9% uptime, the remaining 0.1% (43.8 minutes per month) is your error budget - time you are allowed to fail. Using that budget on planned maintenance, risky deploys, or experiments is not a violation; it is rational allocation of allowed failure. The real problem is not the 0.1% downtime - it is teams that design for 100% uptime and are then paralysed when something breaks because they have no framework for accepting planned failure."

$think015 = Join-Lines @(
    "**Q1.** Your service has SLA = 99.5% (monthly), SLO = 99.9%. Monday, you deploy a risky feature that could improve performance 10%. It has a 1% chance of causing 1-hour outage. Do you deploy? How does error budget inform the decision?",
    "",
    "*Hint:* Think about what deploying a risky feature means for error budget consumption in the worst case (1% chance of 1-hour outage). Calculate the expected error budget burn and compare to remaining budget - then explore whether expected value calculation captures the risk correctly or whether tail risk matters more.",
    "",
    "**Q2.** Your SLI is 99.92% this month - well above SLO (99.9%) and SLA (99.5%). But your P99 latency is 450ms, approaching your SLA limit of 500ms. Should you treat this as all good because uptime is fine, or as a warning sign?",
    "",
    "*Hint:* Think about whether your SLA contract covers uptime only or also latency - is the service responding but slowly a breach? Explore whether P99 latency approaching the SLA limit is a leading indicator that your actual SLA metric will be breached in the future.",
    "",
    "**Q3 (Design Trade-off):** You're designing SLOs for a new microservice that depends on a third-party payment API with SLA = 99.9%. Your service's customer-facing SLA is 99.95%. Is this achievable, and what architectural changes does it force?",
    "",
    "*Hint:* Think about what achievable means when your component's availability ceiling is your dependency's SLA. Explore whether circuit breakers, fallback payment methods, or async payment processing can decouple your availability from the payment API's availability."
)

Upgrade-SYD "SYD-015 - SLA SLO SLI.md" $yaml015 $inv015 $evo015 $rk015 $tw015 $st015 $think015

Write-Host "`nBatch 1b (SYD-011 to SYD-015) complete." -ForegroundColor Cyan
