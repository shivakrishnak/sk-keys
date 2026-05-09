#!/usr/bin/env python3
"""Upgrade MSV-006 through MSV-015 from v2.1 to v3.0."""
import pathlib, re

BASE = pathlib.Path(
    r"c:\ASK\MyWorkspace\sk-keys\dictionary"
    r"\tier-5-distributed-architecture\MSV-microservices"
)

def upgrade(filename, evo, tw_principle, tw_bullets, st,
            q1_hint, q2_hint, q3_text=None, q3_hint=None):
    fp = BASE / filename
    c = fp.read_text(encoding="utf-8")

    # 1. status: draft -> complete, or insert if missing
    if "status: draft" in c:
        c = c.replace("status: draft", "status: complete")
    elif "status: complete" not in c:
        # Insert before the closing --- of the YAML block
        fm_end = c.index("\n---\n", 3)
        c = c[:fm_end] + "\nstatus: complete" + c[fm_end:]

    # 2. Insert EVOLUTION after THE INVENTION MOMENT block
    #    Find "THE INVENTION MOMENT:" then find the next separator "---"
    inv_pos = c.find("**THE INVENTION MOMENT:**")
    if inv_pos >= 0:
        sep_pos = c.find("\n---", inv_pos)
        evo_block = f"\n\n**EVOLUTION:**\n{evo}"
        c = c[:sep_pos] + evo_block + c[sep_pos:]
    else:
        print(f"  WARNING: INVENTION MOMENT not found in {filename}")

    # 3. Build TW + ST content
    tw_block = (
        "### \U0001f48e Transferable Wisdom\n\n"
        f"**Reusable Engineering Principle:**\n{tw_principle}\n\n"
        "**Where else this pattern appears:**\n" + tw_bullets
    )
    st_block = f"### \U0001f4a1 The Surprising Truth\n\n{st}"

    # 4. Find "---\n\n### 🧠 Think" and insert TW + ST before it
    think_header = "### \U0001f9e0 Think About This Before We Continue"
    think_pos = c.find(think_header)
    if think_pos >= 0:
        dash_before = c.rfind("\n---\n", 0, think_pos)
        if dash_before >= 0:
            insert_point = dash_before  # before the \n---\n
            c = (c[:insert_point]
                 + "\n\n---\n\n" + tw_block
                 + "\n\n---\n\n" + st_block
                 + c[insert_point:])
        else:
            print(f"  WARNING: separator before Think not found in {filename}")
    else:
        print(f"  WARNING: Think section not found in {filename}")

    # 5. Insert *Hint:* after Q1, Q2, Q3
    #    Pattern: **Q1.** ... paragraph ... blank line before **Q2.**
    def insert_hint(text, q_marker, next_marker, hint):
        q_pos = text.find(q_marker)
        if q_pos < 0:
            return text
        next_pos = text.find(next_marker, q_pos + len(q_marker))
        if next_pos < 0:
            # Q is the last one - append at end
            text = text.rstrip() + f"\n\n*Hint:* {hint}\n"
            return text
        # Insert hint just before the next_marker (skip blank lines)
        insert_at = text.rfind("\n\n", q_pos, next_pos)
        if insert_at < 0:
            insert_at = next_pos
        text = (text[:insert_at]
                + f"\n\n*Hint:* {hint}"
                + text[insert_at:])
        return text

    c = insert_hint(c, "**Q1.**", "**Q2.**", q1_hint)
    c = insert_hint(c, "**Q2.**", "**Q3.**", q2_hint)

    # If Q3 text provided, append it (file only has Q1+Q2)
    if q3_text:
        c = c.rstrip() + f"\n\n{q3_text}\n\n*Hint:* {q3_hint}\n"
    else:
        # File already has Q3, just add hint at end
        c = insert_hint(c, "**Q3.**", "SENTINEL_NEVER_FOUND", q3_hint)

    fp.write_text(c, encoding="utf-8")
    print(f"OK: {filename}")


# ────────────────────────────────────────────────────────────────────
# MSV-006 - Monolith to Microservices Migration
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-006 - Monolith to Microservices Migration.md",
    evo=(
        "Monolith-to-microservices migration patterns emerged from the near-"
        "100% failure rate of big-bang rewrites documented by practitioners in "
        "the 2000s. The Strangler Fig pattern (Martin Fowler, 2004) provided "
        "the incremental alternative. Netflix's 7-year migration (2008-2015) "
        "from a centralised DVD-rental datacenter to cloud-native microservices "
        "became the canonical case study. Sam Newman's \"Building Microservices\" "
        "(2015) and \"Monolith to Microservices\" (2019) systematized migration "
        "patterns. The discipline evolved from \"extract everything\" to "
        "\"extract by business capability, one domain at a time, driven by "
        "independent deployability requirements.\""
    ),
    tw_principle=(
        "Migrations succeed incrementally or not at all. Any big-bang "
        "replacement of a running system risks the \"new system never catches "
        "up\" failure mode - the original continues accumulating features while "
        "the rewrite struggles to match functionality that took years to build. "
        "The invariant across all successful large-scale migrations: extract "
        "stable, well-bounded domains first; never freeze the old system's "
        "feature development during migration; measure success by reduced "
        "coupling, not by number of services extracted."
    ),
    tw_bullets=(
        "- **Database schema migration:** The anti-pattern is renaming a column "
        "and updating all code simultaneously. The Expand-Contract pattern "
        "(add new column, dual-write, migrate reads, drop old column) is the "
        "incremental equivalent of the Strangler Fig for data.\n"
        "- **Legacy API replacement:** Add new API endpoints alongside old "
        "ones, migrate clients gradually, retire old endpoints last - exactly "
        "the Strangler Fig applied to API surface area.\n"
        "- **UI framework migration:** Replace components incrementally "
        "(React alongside jQuery in the same page) rather than rewriting "
        "the entire frontend at once - the same wrap-and-redirect pattern."
    ),
    st=(
        "The Strangler Fig pattern gets its name from the strangler fig tree "
        "(Ficus aurea), which grows around a host tree over decades, eventually "
        "replacing it entirely while the host continues to live. Martin Fowler "
        "named it after witnessing these trees in Australian rainforests while "
        "thinking about legacy system replacement. The biological metaphor "
        "captures what makes gradual migration succeed: the new system wraps "
        "the old one and receives progressively more traffic until the old system "
        "can be safely removed - without ever shutting it down during the "
        "transition. It is one of the few architecture patterns where the metaphor "
        "is more memorable than the technique itself."
    ),
    q1_hint=(
        "Think about what \"transactional correctness\" means without a "
        "distributed transaction: the three operations become a Saga - each "
        "step is committed independently, with compensating transactions for "
        "rollback on failure. Explore whether the business actually requires "
        "ACID across all three domains or whether a payment-first sequence "
        "(pay, then reserve inventory, then notify) with compensation on failure "
        "is acceptable, and what data integrity gaps exist during the "
        "compensation window."
    ),
    q2_hint=(
        "Think about what objective metrics would answer the CTO's question: "
        "mean time to deploy a single change, number of incidents attributable "
        "to cross-service coupling, velocity trend (accelerating or flat?). "
        "Explore whether the Modular Monolith end state would have delivered "
        "the same deployment independence as the 6 extracted services, without "
        "the operational overhead - and whether the already-extracted services "
        "can be kept as-is while the remaining monolith is refactored to "
        "modules rather than services."
    ),
    q3_hint=(
        "Think about who owns the source of truth for each table in the shared "
        "schema - that determines which strategy preserves correctness. Explore "
        "whether Anti-Corruption Layer (API calls) introduces unacceptable "
        "latency for the JOIN patterns identified, and whether CDC replication "
        "(e.g., Debezium) preserves the query capability while enabling "
        "gradual ownership migration table-by-table."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-007 - On-Premises to Cloud Migration
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-007 - On-Premises to Cloud Migration.md",
    evo=(
        "On-premises to cloud migration began as a cost-reduction initiative "
        "after AWS launched in 2006, with IT teams initially treating cloud as "
        "cheaper hosting. Gartner's 5R (later 6R: Retire, Retain, Rehost, "
        "Replatform, Repurchase, Refactor) framework emerged to structure "
        "migration decisions. Netflix's public documentation of its AWS migration "
        "(2009-2016) demonstrated that cloud-native architecture - not just cloud "
        "hosting - was where the real value lay. The discipline evolved from "
        "\"lift-and-shift everything\" to portfolio analysis: migrate workloads "
        "where cloud offers genuine advantage, retain where cloud creates cost or "
        "compliance problems, and retire workloads that serve no current purpose."
    ),
    tw_principle=(
        "Treat migration as a portfolio decision, not a single technology choice. "
        "Different workloads need different migration strategies based on their "
        "characteristics - age, coupling, compliance requirements, scaling needs. "
        "Applying one strategy (lift-and-shift, or re-architect) to an entire "
        "portfolio is as irrational as investing all capital in one asset class "
        "regardless of market conditions."
    ),
    tw_bullets=(
        "- **Security posture migration:** Not all security controls should move "
        "to cloud-native equivalents simultaneously. Retain on-premises HSMs for "
        "highest-sensitivity keys while migrating application-layer security to "
        "cloud-native IAM - different assets, different migration strategies.\n"
        "- **Data storage tiering:** Hot, warm, and cold data have different "
        "migration priorities and target tiers (S3, S3 Glacier, Glacier Deep "
        "Archive). The same portfolio analysis applies: different data, different "
        "treatment based on access pattern characteristics.\n"
        "- **Team skill migration:** Technical skills don't migrate in a big bang. "
        "Identify the 20% of engineers who learn cloud fastest and make them "
        "migration leads; have them teach the remaining 80% progressively - "
        "portfolio sequencing applied to people, not workloads."
    ),
    st=(
        "The most counterintuitive finding from large-scale cloud migrations is "
        "that the most expensive applications to migrate are often the most "
        "strategically valuable ones. Legacy systems serving critical business "
        "functions were built over decades with hard-won knowledge about edge "
        "cases, regulatory requirements, and business logic - no written "
        "specification exists; the code IS the specification. The applications "
        "cheapest to migrate (stateless, well-documented, commodity workloads) "
        "are often the least strategically valuable. Companies that start with "
        "\"easy wins\" create a portfolio of migrated commodity workloads and a "
        "growing backlog of expensive-but-critical legacy systems. The strategic "
        "migrations always come last and always cost more than budgeted."
    ),
    q1_hint=(
        "Think about what lift-and-shift leaves unchanged that drives cost: "
        "EC2 instances sized for on-premises peak load (over-provisioned 24/7), "
        "data transfer egress costs (no on-premises equivalent), per-vCPU "
        "licensing on more virtual cores than physical cores, and no cloud-native "
        "services (still running self-managed message brokers and databases on "
        "EC2). Explore how rightsizing analysis + cloud-native service adoption "
        "would change the cost model for the 5 largest cost drivers."
    ),
    q2_hint=(
        "Think about what AWS Schema Conversion Tool and DMS actually convert "
        "automatically (DML statements) vs what requires manual effort (complex "
        "PL/SQL stored procedures with Oracle-specific syntax, hints, and "
        "packages). Explore whether a side-by-side dual-run strategy (Oracle and "
        "Aurora both active, application routing by query type) is feasible to "
        "validate query equivalence before cutover, and what the rollback plan "
        "looks like at the cutover window stage."
    ),
    q3_hint=(
        "Think about the latency reality of hybrid: a cross-boundary API call "
        "from cloud to on-premises and back adds at minimum 10-30ms via Direct "
        "Connect vs sub-1ms for intra-cloud calls. Explore whether the 30% "
        "on-premises workloads should be co-located in the nearest AWS Direct "
        "Connect region to minimise cross-boundary latency, and what the "
        "disaster recovery plan is when the Direct Connect circuit has a "
        "maintenance window or failure."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-008 - Technology Migration Strategy
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-008 - Technology Migration Strategy.md",
    evo=(
        "Technology migration became a strategic discipline as software "
        "accumulated technical debt at scale. Martin Fowler's \"Technical Debt\" "
        "concept (1992) gave language to the cost of deferred migration. "
        "Gartner's 6R framework (2011) provided a portfolio decision structure. "
        "Enterprise architects began using wave-based migration (discrete cohorts "
        "with shared infrastructure dependencies resolved first) to manage "
        "sequencing risk. The discipline evolved from \"replace old technology "
        "with new\" to portfolio analysis: assess dependency graphs, sequence "
        "migrations to minimise coupled changes, and measure success by reduced "
        "operational burden rather than technology version numbers."
    ),
    tw_principle=(
        "Sequence changes by dependency, not by ease. The temptation is always "
        "to migrate the \"easy\" systems first and save hard dependencies for "
        "later. But easy systems are easy precisely because they depend on the "
        "hard systems. Migrating easy systems first creates a period where they "
        "run on new technology while their dependencies remain legacy - creating "
        "hybrid complexity without reducing risk. The correct sequence is: "
        "resolve shared dependencies first, then migrate dependents."
    ),
    tw_bullets=(
        "- **Database migration sequencing:** Migrate reporting and analytics "
        "databases (fewer dependents, lower risk) first; use the learnings to "
        "de-risk the transactional database migration that everything else "
        "depends on.\n"
        "- **Framework upgrades:** Upgrade shared libraries (Spring Core, "
        "Hibernate) before application-level components that depend on them. "
        "A framework upgrade that breaks 30 services simultaneously creates "
        "30 concurrent incidents.\n"
        "- **API retirement:** Retire old API versions only after all clients "
        "have migrated, not when the new version launches. The version launch "
        "and retirement are separate events separated by weeks or months."
    ),
    st=(
        "Technology migrations are almost always underestimated by a factor of "
        "2-5x, and the underestimation is structural, not accidental. Teams "
        "estimate the effort to build the new system but systematically omit: "
        "(1) running old and new systems in parallel during the transition, "
        "(2) migrating all existing data and validating its correctness, "
        "(3) updating all tooling, monitoring, and documentation that references "
        "the old system, and (4) transferring institutional knowledge about "
        "the old system's quirks to engineers working on the new one. Items 2-4 "
        "are invisible at planning time and only become visible when you are "
        "deep in the migration and cannot stop."
    ),
    q1_hint=(
        "Think about what migration capacity is taken from: it comes directly "
        "from product feature capacity. At 80% migration / 20% product, "
        "evaluate the compound effect: if the migration takes 50% longer than "
        "planned (typical), you've spent 18 months at minimal product velocity. "
        "Explore whether a 30-40% migration / 60-70% product split produces "
        "better overall outcomes through sustainable pace, and what governance "
        "mechanism prevents the migration percentage creeping upward under "
        "schedule pressure."
    ),
    q2_hint=(
        "Think about what makes rollback triggers unambiguous: they must be "
        "objective (metric + threshold + duration + measurement method, all "
        "pre-agreed), non-negotiable once triggered (override requires a "
        "defined quorum, not the migration team alone), and tested in staging "
        "before the production wave begins. Explore what pre-launch governance "
        "document (rollback authority matrix, pre-agreed override process) "
        "would have prevented the ambiguity you described."
    ),
    q3_hint=(
        "Think about what each model optimises for: centralised decisions "
        "produce consistency but create a bottleneck (all 300 apps queue on "
        "one chief architect); federated decisions produce speed but allow "
        "standards drift across 500 engineers. Explore whether a hybrid model "
        "(federated decisions within centrally-defined guardrails enforced by "
        "automated compliance checks) captures the speed of federated with the "
        "consistency of centralised, and what the guardrails look like in "
        "practice (ADR templates, technology radar, CI/CD policy gates)."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-009 - Re-platforming vs Re-architecting
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-009 - Re-platforming vs Re-architecting.md",
    evo=(
        "The Re-platform / Re-architect distinction emerged from practitioners "
        "discovering that cloud lift-and-shift (Rehost) rarely delivered expected "
        "benefits. Netflix's full re-architecture (not just replatform) to AWS "
        "(2009-2016) demonstrated that cloud-native patterns (auto-scaling, "
        "managed services, event-driven) delivered 10x+ efficiency gains "
        "unavailable to rehosted applications. The discipline evolved from "
        "\"choose one strategy\" to \"apply the right strategy per workload\": "
        "rehost for commodity workloads, replatform for quick cloud benefits, "
        "re-architect for strategic competitive advantages requiring architectural "
        "changes that the current structure cannot accommodate."
    ),
    tw_principle=(
        "Decouple the infrastructure migration from the architecture "
        "transformation. Changing the platform (where code runs) and the "
        "architecture (how code is structured) simultaneously doubles the risk "
        "surface: when something breaks, you cannot distinguish platform bugs "
        "from architecture bugs. The two-step approach - replatform to establish "
        "a known-good cloud baseline, then re-architect within cloud - lets each "
        "step be validated and rolled back independently."
    ),
    tw_bullets=(
        "- **Framework migration:** Replatform (move application to new "
        "container/server infrastructure) before rearchitecting (replace "
        "framework). Each step is independently validatable and reversible.\n"
        "- **Database migration:** Replatform to managed RDS (same database "
        "engine, managed service) before re-architecting to a sharded "
        "microservices data model. Infrastructure change and data model change "
        "are separate risks.\n"
        "- **Team structure changes (Conway's Law):** Replatform team tooling "
        "(Jira, Slack, CI/CD pipelines) before re-architecting team topology. "
        "Tooling changes can be validated before the organisational restructure "
        "introduces coordination complexity."
    ),
    st=(
        "The most common failure mode of re-architecture is called the "
        "\"second system effect\" (Fred Brooks, 1975): engineers who design a "
        "replacement system optimise for features they understand and "
        "systematically underestimate the legacy system's handling of edge cases "
        "accumulated over years. A 10-year-old monolith contains thousands of "
        "implicit business rules in its code that were never written down. The "
        "re-architecture team learns about these rules one production incident at "
        "a time, as each rule they forgot to implement triggers a failure mode "
        "they have never encountered before. The second system is almost always "
        "initially less correct than the system it replaced."
    ),
    q1_hint=(
        "Think about what the new requirements (WebSocket at 500K concurrent, "
        "ML inference per request) technically require that the re-platformed "
        "ECS service cannot provide: stateful connection management (WebSocket "
        "requires sticky sessions or a separate WebSocket gateway), and "
        "inference latency budgets (ML calls need GPU or dedicated inference "
        "instances). Explore whether adding these as new services alongside "
        "the re-platformed monolith (Strangler Fig applied on top of the "
        "re-platform) avoids a full re-architecture of the existing service."
    ),
    q2_hint=(
        "Think about whether the 18-month re-platform investment is truly "
        "\"wasted\" or whether it already delivered value: eliminated on-premises "
        "cost, enabled cloud-managed services, and reduced operational overhead. "
        "Explore whether the 20 apps that need re-architecting can be "
        "re-architected incrementally on top of the existing re-platformed "
        "baseline (not requiring a new infrastructure migration), and what the "
        "total cost is compared to treating the re-platform as wasted and "
        "re-architecting from the original on-premises baseline."
    ),
    q3_hint=(
        "Think about which metrics first become the bottleneck in the monolith "
        "vs re-architected comparison: deployment frequency (currently capped by "
        "monolith coupling?), incident recovery time (full system restart vs "
        "service-level restart?), and team independence (blocked by shared "
        "codebase merge conflicts?). Explore at what team size the overhead of "
        "managing distributed systems is less than the overhead of coordinating "
        "all changes through a single shared codebase."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-010 - Proof of Concept (POC) in Architecture
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-010 - Proof of Concept (POC) in Architecture.md",
    evo=(
        "Proof of Concept became a formal architecture discipline as systems "
        "grew complex enough that architectural risks could not be assessed from "
        "specifications alone. The Architecture Decision Record (ADR) concept "
        "(Michael Nygard, 2011) provided a format for capturing POC outcomes. "
        "Architecture Trade-off Analysis Method (ATAM, Bass et al., 2003) "
        "established criteria for evaluating alternatives before committing. "
        "The discipline evolved from \"build it and see\" to structured risk-"
        "driven experimentation: identify the highest-risk assumption, design "
        "the minimal experiment to validate it, and record results as "
        "architectural decisions that inform future choices."
    ),
    tw_principle=(
        "A POC is a risk-reduction experiment, not a feature prototype. Its "
        "purpose is not to demonstrate what the technology can do, but to "
        "establish that it handles your specific constraints. POCs that prove "
        "only happy-path capability are not architecture validations - they are "
        "demos. The measure of a good POC is the precision of the risk it "
        "eliminates, not the impressiveness of what it builds."
    ),
    tw_bullets=(
        "- **Security design validation:** Before adopting a new authentication "
        "framework, POC the failure modes: what happens when the IdP is "
        "unreachable? What happens to in-flight sessions during certificate "
        "rotation? Validate failure paths, not success paths.\n"
        "- **Data pipeline validation:** Before adopting a stream processing "
        "framework, POC at 110% of peak expected load with realistic message "
        "schemas and consumer lag simulation. Never POC at 50% load with "
        "synthetic data - the risk is at the boundary, not the centre.\n"
        "- **Infrastructure selection:** Before adopting a new database, POC "
        "the backup/restore procedure including time to restore to a consistent "
        "state. Technology that cannot meet RTO in a restore is not a valid "
        "choice regardless of other merits."
    ),
    st=(
        "POCs suffer from a specific cognitive bias: the team that runs the POC "
        "almost always concludes the technology is suitable, even when it is not. "
        "This is not dishonesty - it is the natural result of effort justification "
        "bias. The team spent weeks learning the technology and developing "
        "expertise; concluding the technology is unsuitable means admitting that "
        "investment was wasted. A POC that concludes \"not suitable\" requires "
        "more political courage than a positive conclusion. The mitigation is to "
        "define success and failure criteria, and who has authority to declare "
        "failure, before the POC begins - removing the decision from the team "
        "that ran the experiment."
    ),
    q1_hint=(
        "Think about what the single-consumer-group POC does not test: three "
        "consumer groups competing for the same partitions will rebalance "
        "independently and may produce head-of-line blocking on shared "
        "partitions. The exactly-once semantics overhead also scales with the "
        "number of consumer group transactions. Explore what additional POC "
        "phases (consumer group isolation test, throughput ceiling test at "
        "50K/sec, EOS overhead with 3 concurrent groups) would independently "
        "validate each risk."
    ),
    q2_hint=(
        "Think about what the \"POC was too narrow\" argument means precisely: "
        "did the agreed scope exclude something the senior engineer now claims "
        "is essential? If so, why wasn't that scope in the original criteria? "
        "Explore a governance process where success criteria are locked by all "
        "stakeholders before execution begins, with a formal change request "
        "process for in-flight scope changes that requires explicit sign-off "
        "from all stakeholders - making post-hoc scope expansion visible and "
        "costly."
    ),
    q3_hint=(
        "Think about what makes POC knowledge discoverable: it must be stored "
        "where engineers look when starting new work (linked from the code that "
        "implements the chosen technology, not in a standalone wiki page), "
        "indexed by technology + decision context + outcome, and updated when "
        "the decision is revisited. Explore whether Architecture Decision Records "
        "(ADRs) stored in the code repository alongside the technology they "
        "document are more durable than wiki pages, and what metadata an ADR "
        "needs to be searchable by future engineers."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-011 - Monolith vs Microservices (only Q1, Q2 - add Q3)
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-011 - Monolith vs Microservices.md",
    evo=(
        "The Monolith vs Microservices debate emerged as Amazon's \"two-pizza "
        "team\" philosophy (2002) and Netflix's open-sourcing of microservices "
        "infrastructure (2013-2015) made microservices culturally dominant. "
        "The movement peaked around 2014-2016 when Netflix, Uber, and Airbnb "
        "case studies made microservices appear universally beneficial. DHH's "
        "\"Majestic Monolith\" post (2016) marked the rebalancing: practitioners "
        "began documenting operational complexity costs that success stories "
        "had omitted. The discipline now recognises the decision is context-"
        "dependent: team size, deployment frequency, scaling requirements, and "
        "organisational structure together determine which architecture is correct."
    ),
    tw_principle=(
        "Architecture should reflect organisational structure (Conway's Law). "
        "The best architecture for a given team is the one that maps service "
        "boundaries to team boundaries. A monolith is correct when one team can "
        "own all of it; microservices are correct when independent teams need "
        "independent deployment pipelines. The architectural pattern is a "
        "consequence of the team structure, not the cause of it."
    ),
    tw_bullets=(
        "- **Database design:** A single team owning all tables is fine with a "
        "monolithic schema. Multiple teams sharing a schema without ownership "
        "boundaries creates the shared database anti-pattern - the coupling "
        "problem is the same whether code is a monolith or microservices.\n"
        "- **Deployment pipelines:** A monolith deploys as one unit, which is "
        "fine when all code is always in a consistent state. Multiple services "
        "need independent pipelines - which are overhead unless teams truly "
        "need to deploy on different cadences.\n"
        "- **API contracts:** A monolith can use internal method calls with no "
        "contract. Microservices force all inter-domain communication to explicit "
        "API contracts, which is valuable only when different teams own the "
        "calling and called code and need to evolve independently."
    ),
    st=(
        "The companies most associated with microservices success - Netflix, "
        "Amazon, Uber - all started with monoliths and migrated to microservices "
        "only after reaching scales where the monolith became the bottleneck. "
        "Netflix launched in 2007 as a Java monolith. Uber's early architecture "
        "was a Python monolith. Amazon's legendary two-pizza team structure "
        "emerged after years of operating as a monolith. The microservices "
        "architecture was not the reason these companies scaled - it was the "
        "result of scaling. Engineers who adopt microservices to scale before "
        "they have a scale problem are solving a future problem with a solution "
        "that creates present problems."
    ),
    q1_hint=(
        "Think about what microservices concretely cost at 8 engineers: each "
        "service needs its own deployment pipeline, monitoring dashboards, health "
        "checks, service discovery registration, and on-call runbook. At 8 "
        "engineers, this overhead is borne by the same people writing features. "
        "Explore what specific conditions (independent scaling need, genuinely "
        "different deployment cadences, separate team ownership) would justify "
        "that overhead, and whether any of those conditions apply to a "
        "food-delivery startup at this stage."
    ),
    q2_hint=(
        "Think about which distributed systems failure modes cause reliability "
        "regression that a monolith doesn't have: cascading failures (one slow "
        "service causes thread pool exhaustion in callers), network partition "
        "timeouts (previously fast in-process calls now have milliseconds of "
        "network latency and can fail), and deployment instability (40 services "
        "= 40x the deployment surface area). Explore which specific resilience "
        "patterns (circuit breakers for cascading failure, bulkheads for thread "
        "pool isolation, chaos engineering to find latent failure modes) address "
        "each root cause."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your team extracted 3 services from the "
        "monolith 6 months ago, only to discover the boundaries are wrong: "
        "the 3 services change together 80% of the time and cannot be deployed "
        "independently without careful sequencing. Designing a path forward: "
        "should you merge the 3 services back into one (closer to the original "
        "monolith), redraw boundaries and re-extract, or add an orchestration "
        "layer to manage the sequencing? What data would you gather before "
        "deciding, and how would you avoid the same mistake in the redraw?"
    ),
    q3_hint=(
        "Think about what \"wrong boundaries\" means technically: services that "
        "change together belong in the same service. Explore whether merging the "
        "3 back into a correctly-bounded single service (still smaller than the "
        "original monolith) is simpler than adding orchestration to manage their "
        "sequencing. Consider what the correct decomposition looks like for these "
        "3 domains and whether the error was decomposing by technical layer "
        "rather than by business capability."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-012 - Modular Monolith (only Q1, Q2 - add Q3)
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-012 - Modular Monolith.md",
    evo=(
        "The Modular Monolith emerged as a middle path after practitioners "
        "discovered that unstructured monoliths accumulated coupling while "
        "microservices added operational complexity. Sam Newman introduced the "
        "\"Majestic Monolith\" concept in 2016; Martin Fowler formalised the "
        "concept of explicit internal package boundaries. Shopify's public "
        "documentation (2019) demonstrated that a single Ruby on Rails "
        "application with explicit module boundaries could handle Black Friday "
        "traffic at scale. The discipline evolved from \"it is either a monolith "
        "or microservices\" to recognising that module boundaries, not deployment "
        "boundaries, are what prevent coupling."
    ),
    tw_principle=(
        "Coupling is controlled by explicit interfaces, not deployment "
        "boundaries. A microservice boundary enforces decoupling mechanically - "
        "the only way to call another service is via its network API. A module "
        "boundary enforces decoupling through architectural discipline - calling "
        "another module's private internals is technically possible but "
        "explicitly prohibited. Both approaches reduce coupling; the difference "
        "is enforcement mechanism and operational overhead."
    ),
    tw_bullets=(
        "- **Library design:** A well-designed library with a clear public API "
        "and private internals is a modular monolith at the library level. The "
        "module boundary is the public/private surface, not a network boundary.\n"
        "- **Database schema:** A schema where each module owns its tables and "
        "no cross-module JOINs exist is a modular monolith at the data layer - "
        "the same isolation that microservices enforce via separate databases, "
        "at lower operational cost.\n"
        "- **Event-driven systems:** An in-process event bus within a monolith "
        "decouples modules without network overhead. Each module publishes and "
        "subscribes via the bus - the same pattern as microservices, without "
        "the deployment boundary."
    ),
    st=(
        "Shopify's Modular Monolith handles Black Friday - the highest-traffic "
        "retail event on the internet - on a single Ruby on Rails application "
        "with carefully enforced module boundaries. The application processes "
        "millions of transactions per hour across thousands of merchants. Despite "
        "being a \"monolith,\" it outperforms many microservices architectures in "
        "reliability (no network partition between modules), developer experience "
        "(no inter-service API contracts to version), and infrastructure cost "
        "(no per-service deployment overhead). The Shopify case demonstrates "
        "that \"monolith\" is not a pejorative - an unstructured monolith is a "
        "\"ball of mud,\" but a modular monolith with explicit boundaries can be "
        "both highly scalable and operationally simpler than equivalent "
        "microservices."
    ),
    q1_hint=(
        "Think about what extracting the recommendation engine into a "
        "microservice requires beyond the code change: a new deployment pipeline, "
        "a new API contract with the checkout module, network latency on every "
        "checkout page load, and a separate on-call responsibility. Explore "
        "whether horizontal pod autoscaling of the whole monolith (adding "
        "replicas at peak) would solve the 80% CPU problem with much lower "
        "operational cost, and what conditions (different scaling curves, "
        "different failure budgets, different team ownership) would change "
        "that conclusion."
    ),
    q2_hint=(
        "Think about what measurable criteria indicate further splitting is "
        "justified within a modular monolith: does each proposed sub-module have "
        "a single, distinct reason to change? Do the proposed sub-modules have "
        "meaningfully different change rates (auth changes weekly, profile "
        "changes quarterly)? Do they need different scaling characteristics? "
        "Explore whether those criteria apply to the `users` → 3-module split "
        "and whether the answer changes if the future microservices plan is "
        "locked in (making the split now reduce future migration cost)."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your modular monolith's build time has grown "
        "from 2 minutes to 18 minutes as the codebase expanded to 500K lines. "
        "Engineers avoid refactoring because the feedback loop is too slow. The "
        "team debates: migrate to microservices (independent builds per service) "
        "or invest in build optimisation (incremental compilation, caching). "
        "What data would you gather to make this decision, and what is the "
        "decision framework?"
    ),
    q3_hint=(
        "Think about whether long build times are an architectural problem or a "
        "build tooling problem. Explore whether incremental compilation and build "
        "caching (Gradle build cache, Bazel hermetic builds) can reduce the "
        "monolith build time to under 5 minutes without an architectural change. "
        "Only reach for architectural complexity (microservices) if tooling "
        "cannot solve the feedback loop problem - because microservices solve the "
        "build time problem but introduce distributed systems complexity that "
        "creates new problems."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-013 - Service Decomposition (only Q1, Q2 - add Q3)
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-013 - Service Decomposition.md",
    evo=(
        "Service decomposition became the critical skill in the microservices "
        "era after teams learned that poorly-chosen boundaries created "
        "\"distributed monoliths\" - systems with all the operational complexity "
        "of microservices and none of the independence benefits. Sam Newman's "
        "\"Building Microservices\" (2015) and \"Monolith to Microservices\" "
        "(2019) systematised decomposition patterns. Domain-Driven Design's "
        "Bounded Context concept became the primary theoretical foundation. "
        "The discipline evolved from \"decompose by technical layer\" "
        "(UI/business/data services) to \"decompose by business capability\" - "
        "the only strategy that naturally aligns service boundaries with team "
        "ownership and enables genuine independent deployment."
    ),
    tw_principle=(
        "Decompose by change rate, not by size or functional similarity. The "
        "correct service boundary is where one part changes independently of "
        "another. A service that changes only with its own domain's business "
        "requirements - and never because a different domain changed - is "
        "correctly bounded. Two modules that change together 90% of the time "
        "belong in the same service, regardless of how different their functions "
        "appear."
    ),
    tw_bullets=(
        "- **Database schema design:** Tables that change together (always "
        "updated in the same migration) belong in the same schema. Tables "
        "updated by different teams at different frequencies should have "
        "separate ownership boundaries.\n"
        "- **API design:** API endpoints that version together belong in the "
        "same API definition. Endpoints where one can evolve without breaking "
        "the other should be separate contracts.\n"
        "- **UI component design:** Components with different change rates "
        "(product details updated daily, navigation updated quarterly) should "
        "be independently deployable - the same decomposition principle applied "
        "to frontend components."
    ),
    st=(
        "The most expensive mistake in microservices decomposition is creating "
        "services that map to organisational chart lines rather than business "
        "capability lines. An org chart changes regularly (teams merge, split, "
        "re-assign); business capabilities are stable. A company that creates a "
        "\"Payments Team Service,\" \"Risk Team Service,\" and \"Compliance Team "
        "Service\" will find that when the org restructures, service ownership "
        "no longer matches teams and cross-service changes become the norm. "
        "Services that age best are those decomposed around stable business "
        "capabilities (payment processing, fraud detection, regulatory reporting) "
        "that survive organisational changes intact."
    ),
    q1_hint=(
        "Think about what the data access pattern reveals about the correct "
        "boundary: if every transaction requires reading account balance before "
        "writing the transaction record, and updating the balance is the "
        "transaction's core side effect, then the two concepts are not "
        "independently deployable - they are the same aggregate. Explore whether "
        "the domain rule \"every transaction touches an account\" means "
        "co-located data (same service) or a lookup relationship (different "
        "services with an API call to retrieve balance at transaction time)."
    ),
    q2_hint=(
        "Think about what observable signals confirm services should be merged: "
        "co-deployment rate above 70-80%, co-failure rate (one almost always "
        "fails when the other fails), and the network round-trip between them "
        "being the dominant latency contributor. Explore what \"execute the "
        "merge without downtime\" requires: routing at the load balancer level "
        "(combine service endpoints before combining deployment units), "
        "database schema consolidation (which can be done independently), "
        "and gradual traffic shifting to the merged deployment."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** After decomposing an e-commerce system into "
        "8 services, a performance analysis finds the browse-to-checkout flow "
        "makes 14 synchronous API calls across 6 services. P99 checkout latency "
        "is 3.2 seconds vs 0.4 seconds in the monolith. How do you recover the "
        "latency without merging services back together?"
    ),
    q3_hint=(
        "Think about whether the 14 API calls are sequential (blocking) or can "
        "be parallelised (fan-out). Explore whether an API composition layer "
        "(BFF or GraphQL gateway) that makes all 14 calls in parallel and "
        "assembles the response eliminates sequential latency, and whether some "
        "of the 6 services are fetching data they could cache locally (at the "
        "cost of eventual consistency) rather than calling across service "
        "boundaries on every request."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-014 - Domain-Driven Design (only Q1, Q2 - add Q3)
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-014 - Domain-Driven Design (DDD).md",
    evo=(
        "Domain-Driven Design was formalised by Eric Evans in \"Domain-Driven "
        "Design: Tackling Complexity in the Heart of Software\" (2003), "
        "synthesising patterns from object-oriented design that had been "
        "emerging since the 1990s. DDD gained renewed relevance with "
        "microservices: Bounded Context became the primary tool for defining "
        "service boundaries. Vaughn Vernon's \"Implementing Domain-Driven "
        "Design\" (2013) translated Evans' concepts into practical patterns. "
        "The discipline evolved from a design philosophy for complex OO systems "
        "to the architectural foundation of microservices: Bounded Contexts map "
        "to services, Aggregates define consistency boundaries, and Domain "
        "Events define inter-service communication."
    ),
    tw_principle=(
        "The model IS the design. In DDD, code directly expresses domain "
        "concepts using the language of domain experts. When code drifts from "
        "business language, it becomes harder to reason about and harder to "
        "change correctly - bugs appear at the gap between what the business "
        "says and what the code does. Aligning model language with business "
        "language is not aesthetics; it is correctness."
    ),
    tw_bullets=(
        "- **API design:** REST APIs that use business verbs "
        "(`/orders/{id}/approve`, `/claims/{id}/dispute`) rather than CRUD "
        "verbs (`PUT /orders/{id}`) express domain intent and make the "
        "API self-documenting via the Ubiquitous Language.\n"
        "- **Event naming:** Domain events named after business facts "
        "(`OrderApproved`, `ClaimDisputed`, `AccountSuspended`) rather than "
        "technical operations (`OrderUpdated`, `StatusChanged`) preserve "
        "business meaning for downstream consumers.\n"
        "- **Testing:** Tests named in domain language "
        "(`when_premium_customer_orders_above_threshold_discount_applies`) "
        "rather than implementation language "
        "(`test_calculate_discount_method`) serve as living documentation "
        "of business rules."
    ),
    st=(
        "Eric Evans spent the year after publishing \"Domain-Driven Design\" "
        "realising the book had the patterns in the wrong order. The most "
        "valuable concept - Context Mapping (how Bounded Contexts relate to "
        "each other) - appears in Part IV, near the end. Most practitioners "
        "who read the book stop after Part II (Entity, Value Object, Aggregate) "
        "and never reach Context Mapping. As a result, thousands of teams "
        "implement DDD's tactical patterns without ever implementing its most "
        "important strategic pattern. Evans has publicly said that if he were "
        "writing the book again, he would start with strategic design and "
        "treat tactical patterns as implementation details."
    ),
    q1_hint=(
        "Think about what \"same identity, different data\" means in practice: "
        "the patient has one unique ID across all contexts, but each context "
        "maintains only the attributes it needs (Clinical: diagnosis history; "
        "Billing: insurance IDs; Scheduling: time zone and availability). "
        "Explore which context is the authoritative source for demographic data "
        "and whether a `PatientDemographicChanged` domain event published by "
        "an Identity context and consumed by Clinical, Billing, and Scheduling "
        "would propagate changes without coupling the contexts directly."
    ),
    q2_hint=(
        "Think about the exact sequence in both models for: order placed → "
        "inventory reserved → payment processed. In the consistent model, all "
        "three happen atomically. In the eventual model, each is a separate "
        "domain event. Explore what happens when payment fails after inventory "
        "is already reserved: the Saga pattern (orchestration or choreography "
        "with compensating transactions) must explicitly un-reserve inventory. "
        "Map out what data could be in an incorrect state during the "
        "compensation window and whether the business can tolerate that "
        "inconsistency window."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Your DDD system has 8 bounded contexts, "
        "each with its own model of \"Product\" (different schema, different "
        "status vocabulary, different ownership). A business requirement arrives: "
        "generate a consolidated product report spanning all 8 contexts. "
        "How do you produce the report without coupling the contexts or "
        "introducing a shared product model?"
    ),
    q3_hint=(
        "Think about whether the reporting requirement belongs in a separate "
        "Bounded Context (a Reporting Context) that subscribes to domain events "
        "from all 8 contexts and builds its own denormalised product model "
        "optimised for reporting queries. Explore how CQRS applied at the "
        "cross-context level (all contexts publish events; reporting context "
        "builds a read model) solves the problem without violating context "
        "boundaries, and what the eventual consistency lag means for report "
        "freshness requirements."
    ),
)

# ────────────────────────────────────────────────────────────────────
# MSV-015 - Bounded Context (only Q1, Q2 - add Q3)
# ────────────────────────────────────────────────────────────────────
upgrade(
    "MSV-015 - Bounded Context.md",
    evo=(
        "Bounded Context was introduced by Eric Evans in \"Domain-Driven "
        "Design\" (2003) as the solution to shared models that mean different "
        "things to different teams. As microservices became mainstream "
        "(2013-2016), Bounded Context became the primary tool for defining "
        "service boundaries - providing a theoretical foundation that naive "
        "\"one service per entity\" decomposition had lacked. The discipline "
        "evolved from an OO design concept to the principal architecture pattern "
        "for distributed systems: a Bounded Context defines not just the "
        "language boundary but the ownership boundary, the deployment boundary, "
        "and the consistency boundary of a microservice."
    ),
    tw_principle=(
        "Explicit boundaries enable implicit communication. When boundaries are "
        "undefined, every team has different assumptions about shared concepts - "
        "\"customer\" means something different to billing, fulfillment, and "
        "support without anyone knowing there is a disagreement. When boundaries "
        "are explicit, each team can evolve its model independently while "
        "exposing a clear contract at the boundary. Making implicit assumptions "
        "explicit is the core value of Bounded Contexts."
    ),
    tw_bullets=(
        "- **API versioning:** An API version boundary is a Bounded Context at "
        "the temporal dimension. Different versions coexist without breaking "
        "changes because each version is an explicit boundary with its own "
        "contract and its own consumer set.\n"
        "- **Data warehousing:** A dimensional model (star schema) is a separate "
        "Bounded Context from the operational transactional model. The warehouse "
        "has its own concept of \"customer\" (a denormalised dimension table) "
        "distinct from the OLTP model - this is correct and expected.\n"
        "- **Organisational design:** A team's scope of responsibility is a "
        "Bounded Context at the organisational level. Teams with unbounded "
        "responsibilities (\"everything customer-related\") become bottlenecks "
        "because all other teams need their approval to change anything "
        "in that domain."
    ),
    st=(
        "The most common misconception about Bounded Contexts is that they map "
        "1:1 with microservices. Eric Evans explicitly stated that Bounded "
        "Contexts and microservices are independent concepts: a single "
        "microservice can implement multiple Bounded Contexts, and a single "
        "Bounded Context can span multiple microservices. The confusion arose "
        "because microservices practitioners adopted Bounded Context as their "
        "decomposition tool without reading Evans' nuance. The result: teams "
        "create one microservice per Bounded Context as a rigid rule, producing "
        "either too many tiny services (if contexts are small) or incorrectly "
        "bounded services (if contexts are forced to match service granularity)."
    ),
    q1_hint=(
        "Think about what distinguishes a Shared Kernel (deliberate, governed "
        "joint ownership) from a boundary violation (accidental shared access "
        "with no governance process). Explore what specific evidence to gather: "
        "Is there a joint schema change approval process? Do both teams attend "
        "the same schema review meetings? Is the sharing documented as an "
        "intentional architectural decision? Absence of any of these suggests "
        "an accidental violation, not a shared kernel."
    ),
    q2_hint=(
        "Think about how domain event schema changes break downstream consumers "
        "silently: a new required field causes old consumers to receive an event "
        "with a missing field they don't know to check for; a renamed field "
        "causes old consumers to silently miss the data. Explore whether schema "
        "evolution strategies (semantic versioning on event type names, "
        "backward-compatible additions only, consumer-driven contract testing "
        "via Pact) would prevent the failure modes, and what a schema registry "
        "would add to the solution."
    ),
    q3_text=(
        "**Q3 (Design Trade-off):** Two Bounded Contexts need to share a "
        "concept: the Orders context and the Loyalty context both have a "
        "\"Customer,\" but with different models. A product requirement says "
        "that when a customer places an order, the Loyalty context must update "
        "their points balance in real time - visible on the same confirmation "
        "screen. How do you implement near-real-time cross-context consistency "
        "without coupling the contexts?"
    ),
    q3_hint=(
        "Think about what \"real time\" means from the user's perspective: does "
        "the points balance need to update within the same HTTP response "
        "(requiring synchronous coupling between Orders and Loyalty contexts) "
        "or is an update within 2-3 seconds acceptable after order confirmation "
        "(enabling async domain events)? Explore whether an `OrderPlaced` "
        "domain event published by Orders and consumed by Loyalty can satisfy "
        "the UI requirement if the confirmation screen polls for the updated "
        "loyalty balance after displaying the order confirmation."
    ),
)

print("\nBatch 1 (MSV-006 to MSV-015) complete.")
