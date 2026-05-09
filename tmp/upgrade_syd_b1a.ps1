param()
Set-Location "c:\ASK\MyWorkspace\sk-keys"
$d = "c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SYD-system-design"
$CR = "`r`n"

$gem   = [char]::ConvertFromUtf32(0x1F48E)
$bulb  = [char]::ConvertFromUtf32(0x1F4A1)
$brain = [char]::ConvertFromUtf32(0x1F9E0)
$link  = [char]::ConvertFromUtf32(0x1F517)

function Join-Lines { param([string[]]$lines) return $lines -join $CR }

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

    # 1. Replace YAML (find 2nd ---)
    $fmEnd = $c.IndexOf("---", 4)
    $afterFm = $c.Substring($fmEnd + 3)
    $c = $newYaml + $afterFm

    # 2. Add EVOLUTION after invention moment quote
    if ($c.Contains($inventionMomentQuote)) {
        $c = $c.Replace($inventionMomentQuote, $inventionMomentQuote + $nl + $nl + "**EVOLUTION:**" + $nl + $evolutionText)
    } else { Write-Warning "Invention moment not found in $filename" }

    # 3. Replace Related Keywords section
    $rkHeader = "### $link Related Keywords"
    $rkPos = $c.IndexOf($rkHeader)
    if ($rkPos -ge 0) {
        $afterRk = $c.IndexOf("---", $rkPos + $rkHeader.Length)
        $newRk = $rkHeader + $nl + $nl + $newRelatedContent + $nl + $nl
        $c = $c.Substring(0, $rkPos) + $newRk + $c.Substring($afterRk)
    } else { Write-Warning "Related Keywords not found in $filename" }

    # 4. Insert TW + ST + replace Think section to end of file
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
# SYD-006 - Vertical Scaling
# ============================================================
$yaml006 = Join-Lines @(
    "---",
    "id: SYD-006",
    "title: Vertical Scaling",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: `u{2605}`u{2606}`u{2606}",
    "depends_on: SYD-008, SYD-027",
    "used_by: SYD-007, SYD-014",
    "related: SYD-007, SYD-014, SYD-027",
    "tags:",
    "  - performance",
    "  - architecture",
    "  - foundational",
    "  - distributed",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 6",
    "permalink: /syd/vertical-scaling/",
    "---"
)

$inv006 = '"This is why vertical scaling was created-because sometimes buying one huge machine beats buying ten mediocre ones, at least for a time."'

$evo006 = "Vertical scaling began as the default strategy because early hardware was cheap to upgrade and distributed systems were complex to build. The cloud era changed the economics: auto-provisioned VMs made horizontal scaling accessible to any team. Today, cloud providers offer instances with up to 192 vCPUs and 24 TB of RAM - but per-core costs grow superlinearly at the top of the range. The discipline evolved: vertical scaling is now a deliberate choice for specific workloads - in-memory databases, single-threaded latency-critical services, and legacy monoliths awaiting decomposition - not the default path."

$rk006 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-008 - Load Balancing]] - the infrastructure you'll eventually need when vertical scaling maxes out",
    "- [[SYD-027 - Capacity Planning]] - how to forecast when you'll need to scale",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-007 - Horizontal Scaling]] - the next step when one machine isn't enough",
    "- [[SYD-014 - Auto Scaling]] - automating vertical and horizontal scaling decisions",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-007 - Horizontal Scaling]] - opposite strategy; distribute load across many smaller machines",
    "- [[SYD-027 - Capacity Planning]] - forecast whether vertical can sustain your growth curve"
)

$tw006 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "Every resource has a ceiling. Optimising within one physical boundary buys time but does not remove the boundary. The invariant applies everywhere: a single database, a single process, a single team - all hit ceilings that eventually force a structural change, not just a bigger box.",
    "",
    "**Where else this pattern appears:**",
    "- **Thread pools:** Increasing thread count improves concurrency to a point, then context-switching overhead degrades performance - the same ceiling dynamic.",
    "- **Single-database scaling:** Read replicas and connection pooling extend the ceiling, but eventually you need sharding (horizontal) or a different storage topology.",
    "- **Organisational scaling:** Adding more work to one team is vertical scaling - it works until the communication overhead exceeds the throughput gains."
)

$st006 = "The largest available cloud instances - 192 vCPUs and 24 TB RAM - cost more per unit of compute than a cluster of mid-tier instances. Vertical scaling is not always simpler or cheaper: at the extreme top of the hardware tier, you pay a premium for the physical limitation of fitting more silicon into one rack unit. The point where horizontal becomes economically superior is often lower than engineers expect - typically around 8-16 vCPUs for stateless workloads."

$think006 = Join-Lines @(
    "**Q1.** You're running an e-commerce API on a single ``c5.2xlarge`` instance (8 CPUs, 16 GB RAM). During peak Black Friday traffic, CPU hits 95%, but memory stays at 40%. You have two options: (a) upgrade to ``c5.4xlarge`` (16 CPUs, 32 GB RAM), or (b) add a second instance and set up horizontal scaling with a load balancer. What's the correct choice, and what's the decision framework?",
    "",
    "*Hint:* Think about the time dimension - the spike is immediate, but a new horizontal instance takes minutes to bootstrap and register with the load balancer. Explore what `"in the moment of the spike`" looks like versus `"steady state after scaling.`"",
    "",
    "**Q2.** If your company's technical debt makes horizontal scaling `"impossible right now`" (legacy monolithic code, no session handling), does that mean you can scale vertically indefinitely? What's the hard limit you'll eventually hit, and what does that force you to do?",
    "",
    "*Hint:* Think about what `"impossible right now`" actually means architecturally - what specific property of the monolith (stateful sessions, global shared memory, single database write path) makes horizontal scaling hard, and whether fixing each property requires a rewrite or a targeted refactor.",
    "",
    "**Q3 (Design Trade-off):** Your Java monolith runs on a 96-core machine at 20% average CPU. CPU is projected to hit 95% in 6 months. A microservices rewrite takes 18 months. Should you vertically scale now and plan the rewrite, or start the rewrite immediately and risk the interim period?",
    "",
    "*Hint:* Think about the hard ceiling on your current machine (can you still go bigger?), the risk window during the rewrite, and whether the monolith's database write path is the actual bottleneck rather than CPU."
)

Upgrade-SYD "SYD-006 - Vertical Scaling.md" $yaml006 $inv006 $evo006 $rk006 $tw006 $st006 $think006

# ============================================================
# SYD-007 - Horizontal Scaling
# ============================================================
$yaml007 = Join-Lines @(
    "---",
    "id: SYD-007",
    "title: Horizontal Scaling",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: `u{2605}`u{2606}`u{2606}",
    "depends_on: SYD-006, SYD-008",
    "used_by: SYD-014",
    "related: SYD-006, SYD-008, SYD-014, SYD-027",
    "tags:",
    "  - performance",
    "  - foundational",
    "  - distributed",
    "  - architecture",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 7",
    "permalink: /syd/horizontal-scaling/",
    "---"
)

$inv007 = '"This is why horizontal scaling was created-because at some point, you need to stop scaling UP and start scaling OUT."'

$evo007 = "Horizontal scaling was pioneered at internet scale by Google and Amazon in the mid-2000s, who published papers on Bigtable, Dynamo, and MapReduce as proof that commodity servers could outperform mainframes at a fraction of the cost. The cloud era democratised horizontal scaling: managed load balancers, auto-scaling groups, and container orchestration removed the operational barrier. The discipline evolved from a large-company technique to the default architectural assumption for any stateless service - though making stateful systems horizontally scalable (databases, caches, message queues) remains an active area of distributed systems research."

$rk007 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-006 - Vertical Scaling]] - the single-machine approach; understand before comparing to horizontal",
    "- [[SYD-008 - Load Balancing]] - the infrastructure that makes horizontal scaling possible",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-014 - Auto Scaling]] - automate horizontal scaling based on metrics",
    "- [[SYD-027 - Capacity Planning]] - forecast how many instances you need at each load level",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-006 - Vertical Scaling]] - opposite strategy; upgrade one machine instead of adding more",
    "- [[SYD-028 - Rate Limiting (System)]] - protect the shared bottlenecks that horizontal scaling exposes"
)

$tw007 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "Statelessness is the precondition for horizontal scalability. Any shared mutable state in a component is a horizontal scaling barrier. The principle applies beyond web servers: stateless functions, idempotent message handlers, and side-effect-free API calls are horizontally scalable by default; anything with local state is not.",
    "",
    "**Where else this pattern appears:**",
    "- **Microservices:** Each service should be independently horizontally scalable - which requires stateless design within each service boundary.",
    "- **Lambda/serverless:** Functions scale to thousands of concurrent executions because each invocation is completely stateless by design.",
    "- **Database read replicas:** Read-only queries are stateless relative to write state - they can be distributed horizontally, while writes remain vertically limited."
)

$st007 = "Adding more servers can slow a system down. When horizontal scaling reveals a shared bottleneck - a single database primary, a shared cache with lock contention, or a central message broker - traffic that was previously absorbed by a single slow server now floods the shared resource simultaneously from many fast servers. Teams discover this horizontal scaling inversion when they triple their app server count and response times get worse, not better. The bottleneck was invisible at small scale and only revealed itself when the horizontal layer was fast enough to saturate it."

$think007 = Join-Lines @(
    "**Q1.** You have 10 app servers behind a load balancer, all querying a single database. Traffic increases 5x. You add 50 more app servers. Response times stay slow (2s instead of 100ms). Why didn't adding more servers help, and what should you have done instead?",
    "",
    "*Hint:* Think about where the requests actually spend their time - is the database doing 60 app-server queries in parallel or 1? Explore whether the database is the bottleneck and what architectural change (read replicas, caching, CQRS) addresses the read vs write bottleneck differently.",
    "",
    "**Q2.** Your application stores user sessions in a local in-memory dictionary. You want to horizontally scale it to 10 servers. What architectural changes must you make, and what new failure modes do you introduce by centralizing session state in Redis?",
    "",
    "*Hint:* Think about what happens when the Redis cluster itself becomes unavailable - is a Redis outage worse than a session loss? Explore the trade-off between centralised session durability and the new single point of failure you've introduced.",
    "",
    "**Q3 (First Principles):** Horizontal scaling is often described as stateless scaling. But a shopping cart is stateful. Design a checkout flow that is horizontally scalable without requiring sticky sessions. What architectural decisions does that force?",
    "",
    "*Hint:* Think about where cart state lives (client-side token, external store, or database), what the consistency requirements are between the cart and inventory, and whether eventual consistency is acceptable for a cart that hasn't yet been purchased."
)

Upgrade-SYD "SYD-007 - Horizontal Scaling.md" $yaml007 $inv007 $evo007 $rk007 $tw007 $st007 $think007

# ============================================================
# SYD-008 - Load Balancing
# ============================================================
$yaml008 = Join-Lines @(
    "---",
    "id: SYD-008",
    "title: Load Balancing",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: `u{2605}`u{2605}`u{2606}",
    "depends_on: SYD-007",
    "used_by: SYD-009, SYD-010, SYD-011, SYD-012, SYD-013, SYD-014",
    "related: SYD-009, SYD-010, SYD-011, SYD-012",
    "tags:",
    "  - networking",
    "  - performance",
    "  - foundational",
    "  - distributed",
    "  - architecture",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 8",
    "permalink: /syd/load-balancing/",
    "---"
)

$inv008 = '"This is why load balancers were invented-to stand between clients and servers, distributing traffic intelligently so all servers share the work."'

$evo008 = "Load balancing began as hardware appliances - F5 and Citrix devices costing tens of thousands of dollars, installed in front of server farms. Software load balancers (HAProxy, Nginx) democratised the technique in the 2000s. Cloud providers then made load balancers a managed commodity: AWS ALB/NLB scale to millions of requests per second without operator intervention. The discipline evolved from hardware appliance management to algorithm selection: Layer 4 vs Layer 7, health check configuration, and connection draining now define the practice. Service meshes (Istio, Linkerd) pushed load balancing inside the application network, enabling per-request routing decisions invisible to application code."

$rk008 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-007 - Horizontal Scaling]] - the use case that makes load balancers necessary",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-009 - Round Robin]] - one load balancing algorithm",
    "- [[SYD-010 - Least Connections]] - alternative algorithm for uneven load",
    "- [[SYD-011 - Consistent Hashing (Load Balancing)]] - advanced algorithm for distributed caches",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-012 - Sticky Sessions]] - keeping one client's requests on same server (works with LB)",
    "- [[SYD-013 - Session Affinity]] - similar to sticky sessions; LB-aware routing"
)

$tw008 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "The component that distributes work becomes the component that defines system capacity. Any system with a central dispatcher - a load balancer, a task queue consumer, a thread pool - has its throughput ceiling set by the dispatcher's ability to distribute work without becoming the bottleneck itself. Designing the distributor to be transparent (stateless, fast, horizontally scalable) is the key invariant.",
    "",
    "**Where else this pattern appears:**",
    "- **Database connection pooling:** PgBouncer acts as a load balancer for database connections - distributing application queries across a limited pool of server connections.",
    "- **Message broker consumers:** Kafka consumer groups are a load balancing mechanism - each partition is a server and each consumer is a request handler.",
    "- **DNS round-robin:** The simplest load balancer - return multiple A records for the same domain and let the client pick one."
)

$st008 = "A load balancer does not make a system more available - it makes an already-redundant system more efficient. If you have one server behind a load balancer, the load balancer is a single point of failure and the load balancer-server pair is less available than the server alone. High availability only emerges when at least two healthy servers exist behind the balancer. Teams routinely add load balancers to single-server setups believing they've improved availability, when they've actually added a failure point without adding redundancy."

$think008 = Join-Lines @(
    "**Q1.** A load balancer distributes requests round-robin across 10 servers. One server becomes 10x slower (due to a memory leak). The load balancer still sends it 10% of traffic. What algorithm should you use instead, and why does it solve the problem?",
    "",
    "*Hint:* Think about what metric round robin uses to choose the next server (none - it's position-based) versus what metric least connections or least response time uses. Explore how quickly the alternative algorithm detects and reacts to a degrading server.",
    "",
    "**Q2.** Your load balancer is the single point of failure - if it crashes, all traffic stops. You want HA. Design a redundant load balancing setup. What happens if the Primary LB crashes while a request is mid-flight?",
    "",
    "*Hint:* Think about what mid-flight request means at the TCP level - has the load balancer forwarded the connection to a backend before failing? Explore Active-Active vs Active-Passive LB topologies and what a floating VIP (virtual IP) provides during failover.",
    "",
    "**Q3 (System Interaction):** You have a Layer 4 load balancer (TCP) routing to 10 backend servers. You need to add tenant-based routing: requests from tenant A must go to server group A, and tenant B to server group B. What must change in your architecture, and what are the latency and operational implications?",
    "",
    "*Hint:* Think about what information is available at Layer 4 (IP/port only) vs Layer 7 (HTTP headers, URL path, cookies) and what must be parsed to identify the tenant. Explore whether a service mesh or API gateway can perform this routing without replacing the load balancer."
)

Upgrade-SYD "SYD-008 - Load Balancing.md" $yaml008 $inv008 $evo008 $rk008 $tw008 $st008 $think008

# ============================================================
# SYD-009 - Round Robin
# ============================================================
$yaml009 = Join-Lines @(
    "---",
    "id: SYD-009",
    "title: Round Robin",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: `u{2605}`u{2606}`u{2606}",
    "depends_on: SYD-008, SYD-007",
    "used_by: SYD-010",
    "related: SYD-008, SYD-010, SYD-011",
    "tags:",
    "  - algorithm",
    "  - foundational",
    "  - networking",
    "  - performance",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 9",
    "permalink: /syd/round-robin/",
    "---"
)

$inv009 = '"This is why round robin was created-the simplest fair algorithm: rotate through servers in order."'

$evo009 = "Round robin emerged as the default scheduling algorithm in time-sharing operating systems before it was applied to network load balancing. Hardware load balancers implemented round robin in silicon for maximum throughput. Software implementations (Nginx, HAProxy) added Weighted Round Robin - adjusting the rotation to account for server capacity differences. Modern service meshes extended round robin with jitter and randomisation to prevent synchronised request waves. Today, pure round robin is the baseline that all other load balancing algorithms are measured against - simple enough to reason about, fast enough for most workloads, and wrong enough in specific cases to motivate the study of better algorithms."

$rk009 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-008 - Load Balancing]] - the context where round robin is used as an algorithm",
    "- [[SYD-007 - Horizontal Scaling]] - why you need a load balancing algorithm in the first place",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-010 - Least Connections]] - more sophisticated algorithm that adapts to server state",
    "- [[SYD-011 - Consistent Hashing (Load Balancing)]] - advanced algorithm for distributed systems",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-010 - Least Connections]] - better for requests with varying processing time",
    "- [[SYD-011 - Consistent Hashing (Load Balancing)]] - better when requests have affinity to specific servers"
)

$tw009 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "Uniform distribution without feedback is the simplest fair algorithm, and it is only correct when all recipients are identical and all work items are equal. The moment heterogeneity appears - different server capacities, or different request processing times - round robin produces unfair distribution. Assign equal work to equal workers; use feedback when workers or work items differ.",
    "",
    "**Where else this pattern appears:**",
    "- **Database read replicas:** Applications round-robin across read replicas, but if one replica has replication lag it still receives equal query volume - the same blindness problem.",
    "- **Kubernetes pod scheduling:** kube-scheduler uses a weighted variant of round robin to distribute pods across nodes with different available capacity.",
    "- **Thread pool task assignment:** Java ForkJoinPool uses work-stealing - an adaptive round robin - to rebalance uneven task queues dynamically."
)

$st009 = "Round robin was so effective at time-sharing CPU between processes that it was enshrined in operating system schedulers in the 1960s - decades before the internet. When TCP/IP networking matured and web servers needed to distribute HTTP requests, engineers reached for the algorithm they already knew from OS scheduling. The same 1960s fairness insight that balanced batch jobs on a mainframe became the default for distributing web traffic to server farms - and for many stateless workloads with uniform request profiles, the 60-year-old algorithm is still the correct choice."

$think009 = Join-Lines @(
    "**Q1.** Round robin sends equal traffic to 5 servers. Server 3 has a memory leak - every request leaks 10 MB. After 1 hour, Server 3 is out of memory and crashes. Round robin kept sending it 20% of traffic despite the problem. Should you have used a different algorithm? What would it catch that round robin missed?",
    "",
    "*Hint:* Think about what metric round robin uses to choose the next server (none - it's position-based) versus what metric would detect a degrading server. Explore the difference between detecting a server's health (health checks) and adapting to its current load (least connections).",
    "",
    "**Q2.** A client opens 10 persistent TCP connections and uses them for all future requests (connection pooling). With round robin at the TCP level, these 10 connections might all land on one server. What's the architectural solution - should you change the algorithm or change how clients connect?",
    "",
    "*Hint:* Think about where round robin runs - at the load balancer level for new connections or at the request level - and whether persistent connections bypass per-request distribution. Explore whether shorter connection lifetimes or HTTP/2 multiplexing changes the calculus.",
    "",
    "**Q3 (Comparison):** Round robin and consistent hashing are both load-distribution algorithms. When would you use consistent hashing instead of round robin, and what property of the workload makes the difference?",
    "",
    "*Hint:* Think about whether requests have affinity to a specific server (cached result, session, or shard of data) vs being truly stateless. Explore what cache hit rate looks like on a CDN edge using round robin versus consistent hashing for the same request stream."
)

Upgrade-SYD "SYD-009 - Round Robin.md" $yaml009 $inv009 $evo009 $rk009 $tw009 $st009 $think009

# ============================================================
# SYD-010 - Least Connections
# ============================================================
$yaml010 = Join-Lines @(
    "---",
    "id: SYD-010",
    "title: Least Connections",
    "category: System Design",
    "tier: tier-5-distributed-architecture",
    "folder: SYD-system-design",
    "difficulty: `u{2605}`u{2605}`u{2606}",
    "depends_on: SYD-008, SYD-009",
    "used_by:",
    "related: SYD-009, SYD-008, SYD-011",
    "tags:",
    "  - algorithm",
    "  - intermediate",
    "  - networking",
    "  - performance",
    "status: complete",
    "version: 1",
    "layout: default",
    "parent: `"System Design`"",
    "grand_parent: `"Technical Dictionary`"",
    "nav_order: 10",
    "permalink: /syd/least-connections/",
    "---"
)

$inv010 = '"This is why least connections was created-pick the server with fewest active requests, so slower servers get fewer requests."'

$evo010 = "Least connections was developed as a direct response to round robin's blindness to server load. Early implementations required the load balancer to track active connections in memory - feasible with the small server counts of the 1990s. As server fleets grew to thousands of nodes, tracking per-server connection counts became a distributed coordination problem. Modern implementations use approximate counters with eventual consistency, or delegate to application-layer service mesh sidecar proxies. Least connections is now standard in HAProxy, Nginx, AWS ALB, and Envoy Proxy - and its core insight influenced power-of-two-choices and join-the-shortest-queue algorithms used in hyperscale systems."

$rk010 = Join-Lines @(
    "**Prerequisites (understand these first):**",
    "- [[SYD-008 - Load Balancing]] - the context where this algorithm is applied",
    "- [[SYD-009 - Round Robin]] - the simpler algorithm to compare against",
    "",
    "**Builds On This (learn these next):**",
    "- [[SYD-011 - Consistent Hashing (Load Balancing)]] - advanced algorithm for distributed state routing",
    "",
    "**Alternatives / Comparisons:**",
    "- [[SYD-009 - Round Robin]] - simpler but less adaptive to varying request durations",
    "- [[SYD-011 - Consistent Hashing (Load Balancing)]] - better when client-server affinity matters"
)

$tw010 = Join-Lines @(
    "**Reusable Engineering Principle:**",
    "Feedback-driven distribution outperforms uniform distribution when work items have variable duration. If you have no feedback about the recipient's current state, distribute uniformly; if you have feedback, use it. This is why database connection poolers route to the least-busy server, why Kubernetes considers actual node utilisation when scheduling pods, and why call centres route to the agent with the shortest queue.",
    "",
    "**Where else this pattern appears:**",
    "- **Database connection poolers:** PgBouncer's pool routing prefers idle server connections - a least-connections analogue for database query distribution.",
    "- **Kubernetes scheduling:** The LeastAllocated priority function routes pods to nodes with the most available resources - the resource-based equivalent of least connections.",
    "- **Supermarket checkout:** People naturally join the shortest queue - an emergent least-connections algorithm with imperfect visibility into queue duration."
)

$st010 = "Least connections can be defeated by heavy connections: a single long-running query holding a database connection counts the same as a 1ms API call. A server with one 10-minute connection appears loaded while being almost completely idle in CPU and memory terms. This is why modern algorithms track not just connection count but connection age, latency, or pending request count separately. HAProxy's leastconn algorithm weights active connections higher than idle ones - but most engineers assume it simply counts all open sockets equally, leading to misconfigured pools under long-running workloads."

$think010 = Join-Lines @(
    "**Q1.** Least connections routes to the server with minimum active connections. If Server 1 becomes unresponsive (hanging connections never close), its connection count rises indefinitely. LC stops routing to it (good), but those hanging connections never drain. How is this problem solved in practice - what mechanism closes them?",
    "",
    "*Hint:* Think about what happens to a connection's count when it hangs - does it stay open indefinitely, and does the connection count ever decrease on its own? Explore TCP keepalive, idle timeout, and the difference between a connection the OS considers open and one the application considers active.",
    "",
    "**Q2.** Connection pooling: a client opens 10 persistent connections to the LB. Each initially goes to a different server via LC. Now all future requests on each connection stick to that server. Is LC broken, or is this the correct behaviour? Should the LB rebalance mid-connection?",
    "",
    "*Hint:* Think about whether LC is a per-request decision or a per-connection decision - once a connection is established (pinned to a server), does LC continue influencing which server subsequent requests go to? Explore whether HTTP/2 multiplexing makes this question irrelevant for modern traffic.",
    "",
    "**Q3 (Failure Mode):** A server in your least-connections pool has a memory leak. Every request increases memory by 10 MB but the request completes normally - connections drop to zero after each request. After 1,000 requests the server is OOM and starts returning 500s. Does least connections protect you, and why or why not?",
    "",
    "*Hint:* Think about what metric least connections tracks (active connections) versus what metric reveals a memory leak (memory utilisation, error rate, response time). Explore what health check configuration would detect the server's degradation before it reaches OOM."
)

Upgrade-SYD "SYD-010 - Least Connections.md" $yaml010 $inv010 $evo010 $rk010 $tw010 $st010 $think010

Write-Host "`nBatch 1a (SYD-006 to SYD-010) complete." -ForegroundColor Cyan
