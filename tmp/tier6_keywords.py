"""Tier-6: Infrastructure & DevOps — 11 categories"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tier_shift_lib import process_shift, process_full

BASE = pathlib.Path(r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-6-infrastructure-devops")

META = {
    "CTR": dict(category="Containers", tier="tier-6-infrastructure-devops",
                folder="CTR-containers", parent="Containers",
                dir=BASE / "CTR-containers"),
    "K8S": dict(category="Kubernetes", tier="tier-6-infrastructure-devops",
                folder="K8S-kubernetes", parent="Kubernetes",
                dir=BASE / "K8S-kubernetes"),
    "AWS": dict(category="Cloud -- AWS", tier="tier-6-infrastructure-devops",
                folder="AWS-cloud-aws", parent="Cloud -- AWS",
                dir=BASE / "AWS-cloud-aws"),
    "AZR": dict(category="Cloud -- Azure", tier="tier-6-infrastructure-devops",
                folder="AZR-cloud-azure", parent="Cloud -- Azure",
                dir=BASE / "AZR-cloud-azure"),
    "CCD": dict(category="CI/CD", tier="tier-6-infrastructure-devops",
                folder="CCD-cicd", parent="CI/CD",
                dir=BASE / "CCD-cicd"),
    "GIT": dict(category="Git & Branching Strategy", tier="tier-6-infrastructure-devops",
                folder="GIT-git-branching", parent="Git & Branching Strategy",
                dir=BASE / "GIT-git-branching"),
    "MVN": dict(category="Maven & Build Tools", tier="tier-6-infrastructure-devops",
                folder="MVN-maven-build", parent="Maven & Build Tools",
                dir=BASE / "MVN-maven-build"),
    "CDQ": dict(category="Code Quality", tier="tier-6-infrastructure-devops",
                folder="CDQ-code-quality", parent="Code Quality",
                dir=BASE / "CDQ-code-quality"),
    "TST": dict(category="Testing", tier="tier-6-infrastructure-devops",
                folder="TST-testing", parent="Testing",
                dir=BASE / "TST-testing"),
    "OBS": dict(category="Observability & SRE", tier="tier-6-infrastructure-devops",
                folder="OBS-observability-sre", parent="Observability & SRE",
                dir=BASE / "OBS-observability-sre"),
    "IAC": dict(category="Infrastructure as Code", tier="tier-6-infrastructure-devops",
                folder="IAC-infrastructure-code", parent="Infrastructure as Code",
                dir=BASE / "IAC-infrastructure-code"),
}

# ── CTR (37 files → 006..042) ─────────────────────────────────────────────
process_shift("CTR", META["CTR"],
    l0_titles=[
        "What Is Containerization and Why It Matters",
        "VMs vs Containers -- A Mental Model",
        "The Container Ecosystem Map",
        "Why Docker Changed Everything",
        "Containers in Production -- What to Expect",
    ],
    l45_titles=[
        "Container Platform Strategy",
        "Container Security Architecture",
        "Container Image Strategy at Scale",
        "Containerization Migration Strategy",
        "Multi-Runtime Container Strategy (containerd, CRI-O)",
    ],
    l5_titles=[
        "Container Runtime Internals (runc, containerd)",
        "Linux Namespace and Cgroup Architecture",
        "Container Image Format Design (OCI)",
        "Container Security Research (Rootless, gVisor)",
    ],
    meta_titles=[
        "Container Trade-off Framing",
        "Containerization Necessity Assessment",
        "Container Security Mental Model",
    ],
)

# ── K8S (60 files → 006..065) ─────────────────────────────────────────────
process_shift("K8S", META["K8S"],
    l0_titles=[
        "What Is Kubernetes and Why It Exists",
        "The Kubernetes Mental Model (Desired State)",
        "Kubernetes vs Docker Swarm vs Mesos",
        "The Kubernetes Ecosystem Map",
        "Kubernetes in Production -- What to Expect",
    ],
    l45_titles=[
        "Kubernetes Cluster Architecture Strategy",
        "Kubernetes Multi-Cluster Strategy",
        "Kubernetes Cost Optimization Strategy",
        "Kubernetes Security Architecture",
        "Platform Engineering with Kubernetes",
    ],
    l5_titles=[
        "Kubernetes Controller and Operator Design",
        "etcd and Consensus in Kubernetes",
        "Kubernetes Scheduler Algorithm Design",
        "Kubernetes API Extension Points",
    ],
    meta_titles=[
        "Kubernetes Trade-off Framing",
        "Cluster Design Mental Model",
        "Kubernetes Necessity Assessment",
    ],
)

# ── AWS (60 files → 006..065) ─────────────────────────────────────────────
process_shift("AWS", META["AWS"],
    l0_titles=[
        "What Is AWS and the Cloud Model",
        "The AWS Service Landscape -- A Map",
        "Cloud vs On-Premise -- Real Trade-offs",
        "AWS Well-Architected Framework",
        "The AWS Ecosystem Map",
    ],
    l45_titles=[
        "AWS Architecture Strategy (Multi-AZ, Multi-Region)",
        "AWS Cost Optimization Framework",
        "AWS Security Architecture",
        "AWS Migration Strategy (6 Rs)",
        "AWS Platform Engineering",
    ],
    l5_titles=[
        "AWS Service Internals Deep Dives",
        "Cloud-Native Architecture Design",
        "AWS Infrastructure as Code at Scale",
        "AWS Novel Service Patterns Research",
    ],
    meta_titles=[
        "Cloud Trade-off Framing",
        "AWS Service Selection Mental Model",
        "Cloud Cost Mental Model",
    ],
)

# ── AZR (0 files — full list, 55 keywords) ────────────────────────────────
AZR_KEYWORDS = [
    # L0
    ("AZR-001", None, "What Is Azure and the Microsoft Cloud", "L0", "🌱"),
    ("AZR-002", None, "The Azure Service Landscape -- A Map", "L0", "🌱"),
    ("AZR-003", None, "Azure vs AWS vs GCP -- Key Differences", "L0", "🌱"),
    ("AZR-004", None, "Azure Well-Architected Framework", "L0", "🌱"),
    ("AZR-005", None, "The Azure Ecosystem Map", "L0", "🌱"),
    # L1
    ("AZR-006", None, "Azure Regions and Availability Zones", "L1", "★☆☆"),
    ("AZR-007", None, "Azure Resource Manager (ARM)", "L1", "★☆☆"),
    ("AZR-008", None, "Azure Subscriptions and Resource Groups", "L1", "★☆☆"),
    ("AZR-009", None, "Azure Active Directory (Entra ID)", "L1", "★☆☆"),
    ("AZR-010", None, "Azure Virtual Machines", "L1", "★☆☆"),
    ("AZR-011", None, "Azure App Service", "L1", "★☆☆"),
    ("AZR-012", None, "Azure Blob Storage", "L1", "★☆☆"),
    ("AZR-013", None, "Azure SQL Database", "L1", "★☆☆"),
    # L2
    ("AZR-014", None, "Azure Virtual Network (VNet)", "L2", "★★☆"),
    ("AZR-015", None, "Azure Load Balancer and Application Gateway", "L2", "★★☆"),
    ("AZR-016", None, "Azure Kubernetes Service (AKS)", "L2", "★★☆"),
    ("AZR-017", None, "Azure Container Instances", "L2", "★★☆"),
    ("AZR-018", None, "Azure Functions (Serverless)", "L2", "★★☆"),
    ("AZR-019", None, "Azure Service Bus", "L2", "★★☆"),
    ("AZR-020", None, "Azure Event Hub", "L2", "★★☆"),
    ("AZR-021", None, "Azure Cosmos DB", "L2", "★★☆"),
    ("AZR-022", None, "Azure Key Vault", "L2", "★★☆"),
    ("AZR-023", None, "Azure DevOps (Pipelines, Boards)", "L2", "★★☆"),
    ("AZR-024", None, "Azure Monitor and Log Analytics", "L2", "★★☆"),
    ("AZR-025", None, "Azure CDN and Front Door", "L2", "★★☆"),
    # L3
    ("AZR-026", None, "Azure API Management", "L3", "★★☆"),
    ("AZR-027", None, "Azure Service Fabric", "L3", "★★☆"),
    ("AZR-028", None, "Azure Cache for Redis", "L3", "★★☆"),
    ("AZR-029", None, "Azure Cognitive Services and OpenAI", "L3", "★★☆"),
    ("AZR-030", None, "Azure Synapse Analytics", "L3", "★★☆"),
    ("AZR-031", None, "Azure Data Factory", "L3", "★★☆"),
    ("AZR-032", None, "Azure Event Grid", "L3", "★★☆"),
    ("AZR-033", None, "Azure Logic Apps", "L3", "★★☆"),
    ("AZR-034", None, "Azure Managed Identity", "L3", "★★☆"),
    ("AZR-035", None, "Azure Policy and RBAC", "L3", "★★☆"),
    ("AZR-036", None, "Azure Private Endpoint", "L3", "★★☆"),
    ("AZR-037", None, "Azure Terraform Integration", "L3", "★★☆"),
    ("AZR-038", None, "Azure Bicep (IaC)", "L3", "★★☆"),
    # L4
    ("AZR-039", None, "Azure Security Center (Defender)", "L4", "★★★"),
    ("AZR-040", None, "Azure Landing Zone Architecture", "L4", "★★★"),
    ("AZR-041", None, "Azure Multi-Region Deployment", "L4", "★★★"),
    ("AZR-042", None, "Azure ExpressRoute and VPN Gateway", "L4", "★★★"),
    ("AZR-043", None, "Azure Cost Management and Optimization", "L4", "★★★"),
    ("AZR-044", None, "Azure Site Recovery (DR)", "L4", "★★★"),
    ("AZR-045", None, "Azure Arc (Hybrid Cloud)", "L4", "★★★"),
    ("AZR-046", None, "Azure Observability Strategy", "L4", "★★★"),
    # L4.5
    ("AZR-047", None, "Azure Architecture Strategy (Enterprise)", "L45", "🔥"),
    ("AZR-048", None, "Azure Migration Strategy", "L45", "🔥"),
    ("AZR-049", None, "Azure Platform Engineering Strategy", "L45", "🔥"),
    ("AZR-050", None, "Azure vs AWS Selection Framework", "L45", "🔥"),
    # L5
    ("AZR-051", None, "Azure Service Internals Deep Dives", "L5", "🔬"),
    ("AZR-052", None, "Cloud-Native Architecture on Azure", "L5", "🔬"),
    ("AZR-053", None, "Azure Research and Novel Patterns", "L5", "🔬"),
    # META
    ("AZR-054", None, "Azure Service Selection Mental Model", "META", "🧠"),
    ("AZR-055", None, "Cloud Cost Mental Model (Azure)", "META", "🧠"),
]
process_full("AZR", META["AZR"], AZR_KEYWORDS)

# ── CCD (66 files → 006..071) ─────────────────────────────────────────────
process_shift("CCD", META["CCD"],
    l0_titles=[
        "What Is CI/CD and Why It Matters",
        "The Software Delivery Lifecycle -- A Map",
        "Manual vs Automated Deployment",
        "The CI/CD Ecosystem Map (Jenkins, GitHub Actions, GitLab)",
        "CI/CD in Production -- What to Expect",
    ],
    l45_titles=[
        "CI/CD Pipeline Architecture Design",
        "Release Strategy Design (Blue-Green, Canary)",
        "Pipeline Security Architecture (DevSecOps)",
        "Multi-Environment Deployment Strategy",
        "Platform Engineering CI/CD Strategy",
    ],
    l5_titles=[
        "Continuous Delivery Principles (Jez Humble)",
        "Pipeline as Code Design Patterns",
        "Deployment Pipeline Research",
        "GitOps Architecture Design",
    ],
    meta_titles=[
        "Deployment Trade-off Framing",
        "Pipeline Design Mental Model",
        "Automation Necessity Assessment",
    ],
)

# ── GIT (0 files — full list, 45 keywords) ────────────────────────────────
GIT_KEYWORDS = [
    # L0
    ("GIT-001", None, "What Is Git and Why Version Control Matters", "L0", "🌱"),
    ("GIT-002", None, "The Git Mental Model (DAG of Commits)", "L0", "🌱"),
    ("GIT-003", None, "Git vs Other VCS (SVN, Mercurial)", "L0", "🌱"),
    ("GIT-004", None, "The Git Ecosystem Map (GitHub, GitLab, Bitbucket)", "L0", "🌱"),
    ("GIT-005", None, "Git in Teams -- What to Expect", "L0", "🌱"),
    # L1
    ("GIT-006", None, "Git Basics (init, clone, add, commit, push, pull)", "L1", "★☆☆"),
    ("GIT-007", None, "Git Staging Area (Index)", "L1", "★☆☆"),
    ("GIT-008", None, "Git Branches -- Create, Switch, Delete", "L1", "★☆☆"),
    ("GIT-009", None, "Git Merge", "L1", "★☆☆"),
    ("GIT-010", None, "Git Rebase", "L1", "★☆☆"),
    ("GIT-011", None, "Git Conflict Resolution", "L1", "★☆☆"),
    ("GIT-012", None, "Git Remote (origin, upstream)", "L1", "★☆☆"),
    ("GIT-013", None, ".gitignore", "L1", "★☆☆"),
    # L2
    ("GIT-014", None, "Git Stash", "L2", "★★☆"),
    ("GIT-015", None, "Git Tags (Lightweight and Annotated)", "L2", "★★☆"),
    ("GIT-016", None, "Git Cherry-Pick", "L2", "★★☆"),
    ("GIT-017", None, "Git Bisect", "L2", "★★☆"),
    ("GIT-018", None, "Git Hooks", "L2", "★★☆"),
    ("GIT-019", None, "Git Submodules", "L2", "★★☆"),
    ("GIT-020", None, "Pull Requests and Code Review Workflow", "L2", "★★☆"),
    ("GIT-021", None, "Git Log and History Exploration", "L2", "★★☆"),
    ("GIT-022", None, "Branching Strategies Overview", "L2", "★★☆"),
    # L3
    ("GIT-023", None, "GitFlow Strategy", "L3", "★★☆"),
    ("GIT-024", None, "Trunk-Based Development", "L3", "★★☆"),
    ("GIT-025", None, "GitHub Flow", "L3", "★★☆"),
    ("GIT-026", None, "Feature Flags and Branch by Abstraction", "L3", "★★☆"),
    ("GIT-027", None, "Commit Message Conventions (Conventional Commits)", "L3", "★★☆"),
    ("GIT-028", None, "Semantic Versioning (SemVer)", "L3", "★★☆"),
    ("GIT-029", None, "Git Reflog -- Recovery from Mistakes", "L3", "★★☆"),
    ("GIT-030", None, "Monorepo vs Polyrepo Strategy", "L3", "★★☆"),
    ("GIT-031", None, "Git Large File Storage (LFS)", "L3", "★★☆"),
    # L4
    ("GIT-032", None, "Git Internals -- Objects, Trees, Blobs", "L4", "★★★"),
    ("GIT-033", None, "Git Packfiles and Delta Compression", "L4", "★★★"),
    ("GIT-034", None, "GitOps Fundamentals", "L4", "★★★"),
    ("GIT-035", None, "Signed Commits and GPG Verification", "L4", "★★★"),
    ("GIT-036", None, "Repository Security -- Supply Chain Risks", "L4", "★★★"),
    # L4.5
    ("GIT-037", None, "Branching Strategy Selection Framework", "L45", "🔥"),
    ("GIT-038", None, "Monorepo Architecture Strategy", "L45", "🔥"),
    ("GIT-039", None, "GitOps Architecture Design", "L45", "🔥"),
    # L5
    ("GIT-040", None, "Git Protocol and Data Format Internals", "L5", "🔬"),
    ("GIT-041", None, "Distributed Version Control Theory", "L5", "🔬"),
    ("GIT-042", None, "Git Performance at Scale", "L5", "🔬"),
    # META
    ("GIT-043", None, "Branch Strategy Trade-off Framing", "META", "🧠"),
    ("GIT-044", None, "Git History Mental Model", "META", "🧠"),
    ("GIT-045", None, "Repository Design Thinking", "META", "🧠"),
]
process_full("GIT", META["GIT"], GIT_KEYWORDS)

# ── MVN (30 files → 006..035) ─────────────────────────────────────────────
process_shift("MVN", META["MVN"],
    l0_titles=[
        "What Is a Build Tool and Why It Matters",
        "The Build Tool Ecosystem Map (Maven, Gradle, Ant)",
        "Build vs Compile vs Package vs Deploy",
        "Dependency Management Mental Model",
        "Maven in the Java Ecosystem",
    ],
    l45_titles=[
        "Build Tool Selection Strategy (Maven vs Gradle)",
        "Monorepo Build Strategy",
        "Build Performance Optimization",
        "Dependency Security Strategy",
        "Build Pipeline Architecture",
    ],
    l5_titles=[
        "Build Tool Internals (Gradle DAG, Maven Lifecycle)",
        "Custom Plugin Design",
        "Build Cache Architecture",
        "Build Hermiticity Research",
    ],
    meta_titles=[
        "Dependency Mental Model",
        "Build Trade-off Framing",
        "Build Performance Intuition",
    ],
)

# ── CDQ (25 files → 006..030) ─────────────────────────────────────────────
process_shift("CDQ", META["CDQ"],
    l0_titles=[
        "What Is Code Quality and Why It Matters",
        "The Code Quality Landscape -- A Map",
        "Technical Debt -- A Mental Model",
        "Code Quality vs Velocity Trade-off",
        "The Code Quality Ecosystem Map (SonarQube, Checkstyle)",
    ],
    l45_titles=[
        "Code Quality Architecture (Quality Gates)",
        "Technical Debt Strategy",
        "Code Review Process Design",
        "Static Analysis at Scale",
        "Engineering Excellence Program Design",
    ],
    l5_titles=[
        "Software Quality Measurement Research",
        "Formal Verification Approaches",
        "Program Analysis Theory",
        "Software Reliability Engineering Metrics",
    ],
    meta_titles=[
        "Quality Trade-off Framing",
        "Technical Debt Mental Model",
        "Code Review Mindset",
    ],
)

# ── TST (54 files → 006..059) ─────────────────────────────────────────────
process_shift("TST", META["TST"],
    l0_titles=[
        "Why Testing Matters -- The Cost of Bugs",
        "The Testing Landscape -- A Map",
        "Test Pyramid Mental Model",
        "Manual vs Automated Testing",
        "The Testing Ecosystem Map",
    ],
    l45_titles=[
        "Testing Strategy Architecture",
        "Test Automation Strategy at Scale",
        "Shift-Left Testing Design",
        "Contract Testing Architecture",
        "Quality Engineering Strategy",
    ],
    l5_titles=[
        "Testing Theory (Mutation Testing, Property-Based Testing)",
        "Test Specification Formal Methods",
        "Testing Research Frontiers",
        "Chaos Engineering Design",
    ],
    meta_titles=[
        "Testing Trade-off Framing",
        "Test Coverage Mental Model",
        "Testing ROI Thinking",
    ],
)

# ── OBS (6 files — full list, 60 keywords) ────────────────────────────────
# Keep 6 existing, add full curriculum
OBS_KEYWORDS = [
    # L0
    ("OBS-001", None, "What Is Observability and Why It Matters", "L0", "🌱"),
    ("OBS-002", None, "The Three Pillars of Observability (Logs, Metrics, Traces)", "L0", "🌱"),
    ("OBS-003", None, "Monitoring vs Observability -- The Difference", "L0", "🌱"),
    ("OBS-004", None, "The Observability Ecosystem Map", "L0", "🌱"),
    ("OBS-005", None, "SRE -- What It Is and Why It Exists", "L0", "🌱"),
    # L1
    ("OBS-006", None, "Metrics -- Types (Counter, Gauge, Histogram)", "L1", "★☆☆"),
    ("OBS-007", None, "Logging Fundamentals (Structured Logs)", "L1", "★☆☆"),
    ("OBS-008", None, "Distributed Tracing Fundamentals", "L1", "★☆☆"),
    ("OBS-009", None, "Alerting Fundamentals", "L1", "★☆☆"),
    ("OBS-010", None, "Dashboards and Visualization Basics", "L1", "★☆☆"),
    ("OBS-011", None, "SLI (Service Level Indicator)", "L1", "★☆☆"),
    ("OBS-012", None, "SLO (Service Level Objective)", "L1", "★☆☆"),
    ("OBS-013", None, "SLA (Service Level Agreement)", "L1", "★☆☆"),
    # L2
    ("OBS-014", None, "Prometheus -- Metrics Collection", "L2", "★★☆"),
    ("OBS-015", None, "Grafana -- Dashboards", "L2", "★★☆"),
    ("OBS-016", None, "OpenTelemetry -- The Standard", "L2", "★★☆"),
    ("OBS-017", None, "Jaeger / Zipkin -- Distributed Tracing", "L2", "★★☆"),
    ("OBS-018", None, "ELK / EFK Stack -- Log Management", "L2", "★★☆"),
    ("OBS-019", None, "Error Budget", "L2", "★★☆"),
    ("OBS-020", None, "Alerting Anti-Patterns (Alert Fatigue)", "L2", "★★☆"),
    ("OBS-021", None, "Health Check Patterns", "L2", "★★☆"),
    ("OBS-022", None, "AWS CloudWatch Dashboards", "L2", "★★☆"),
    ("OBS-023", None, "AWS CloudWatch Log Insights", "L2", "★★☆"),
    # L3
    ("OBS-024", None, "AWS CloudWatch Alarms", "L3", "★★☆"),
    ("OBS-025", None, "AWS X-Ray (Distributed Tracing)", "L3", "★★☆"),
    ("OBS-026", None, "Actionable Alerting Patterns", "L3", "★★☆"),
    ("OBS-027", None, "AppDynamics -- APM", "L3", "★★☆"),
    ("OBS-028", None, "Datadog -- Observability Platform", "L3", "★★☆"),
    ("OBS-029", None, "Dynatrace -- Full-Stack Monitoring", "L3", "★★☆"),
    ("OBS-030", None, "Incident Management Process", "L3", "★★☆"),
    ("OBS-031", None, "Runbooks and Playbooks", "L3", "★★☆"),
    ("OBS-032", None, "Log Aggregation at Scale", "L3", "★★☆"),
    ("OBS-033", None, "Trace Sampling Strategies", "L3", "★★☆"),
    ("OBS-034", None, "RED Method (Rate, Errors, Duration)", "L3", "★★☆"),
    ("OBS-035", None, "USE Method (Utilization, Saturation, Errors)", "L3", "★★☆"),
    ("OBS-036", None, "Golden Signals", "L3", "★★☆"),
    # L4
    ("OBS-037", None, "Cardinality in Metrics Systems", "L4", "★★★"),
    ("OBS-038", None, "Continuous Profiling (Pyroscope, Parca)", "L4", "★★★"),
    ("OBS-039", None, "eBPF for Observability", "L4", "★★★"),
    ("OBS-040", None, "Chaos Engineering for Observability", "L4", "★★★"),
    ("OBS-041", None, "Post-Mortem and Blameless Culture", "L4", "★★★"),
    ("OBS-042", None, "Toil Reduction Strategy", "L4", "★★★"),
    ("OBS-043", None, "Capacity Planning with Metrics", "L4", "★★★"),
    ("OBS-044", None, "Observability at Scale (Sampling, Aggregation)", "L4", "★★★"),
    ("OBS-045", None, "SRE Book -- Core Principles Deep Dive", "L4", "★★★"),
    # L4.5
    ("OBS-046", None, "Observability Platform Architecture Design", "L45", "🔥"),
    ("OBS-047", None, "SLO-Based Alerting Strategy", "L45", "🔥"),
    ("OBS-048", None, "Observability-Driven Development Strategy", "L45", "🔥"),
    ("OBS-049", None, "Platform Observability Engineering", "L45", "🔥"),
    # L5
    ("OBS-050", None, "Observability System Design Internals", "L5", "🔬"),
    ("OBS-051", None, "Time-Series Database Design", "L5", "🔬"),
    ("OBS-052", None, "Distributed Tracing System Architecture", "L5", "🔬"),
    ("OBS-053", None, "Formal SLO Theory", "L5", "🔬"),
    # META
    ("OBS-054", None, "Observability-First Thinking", "META", "🧠"),
    ("OBS-055", None, "SLO Trade-off Framing", "META", "🧠"),
    ("OBS-056", None, "Reliability Mental Model", "META", "🧠"),
]
# Re-map the 6 existing OBS files to their rightful slots
# OBS-001=AppDynamics → now OBS-027, OBS-002=CloudWatch Alarms → OBS-024,
# OBS-003=CloudWatch Dashboards → OBS-022, OBS-004=CloudWatch Log Insights → OBS-023,
# OBS-005=AWS X-Ray → OBS-025, OBS-006=Actionable Alerting → OBS-026
import re, pathlib as _pl
_obs_dir = _pl.Path(META["OBS"]["dir"])
_remap = {
    "OBS-001": "OBS-027",  # AppDynamics
    "OBS-002": "OBS-024",  # CloudWatch Alarms
    "OBS-003": "OBS-022",  # CloudWatch Dashboards
    "OBS-004": "OBS-023",  # CloudWatch Log Insights
    "OBS-005": "OBS-025",  # X-Ray
    "OBS-006": "OBS-026",  # Actionable Alerting
}
for f in list(_obs_dir.glob("OBS-00[1-6] *.md")):
    m = re.match(r"(OBS-\d+)", f.stem)
    if m and m.group(1) in _remap:
        tmp = f.parent / f"_tmp_{_remap[m.group(1)]}_{f.name}"
        f.rename(tmp)
for tmp in _obs_dir.glob("_tmp_OBS-*.md"):
    m = re.search(r"_tmp_(OBS-\d+)_", tmp.name)
    if m:
        new_id = m.group(1)
        # Get original filename
        orig = re.sub(r"^_tmp_OBS-\d+_", "", tmp.name)
        orig_id_m = re.match(r"(OBS-\d+)", orig)
        if orig_id_m:
            orig_id = orig_id_m.group(1)
            title_part = re.sub(rf"^{re.escape(orig_id)}\s+[—\-]\s*", "", tmp.stem.replace(f"_tmp_{new_id}_","").replace(f"{orig_id} — ",""))
            new_name = f"{new_id} \u2014 {title_part}.md"
            dst = tmp.parent / new_name
            tmp.rename(dst)
            print(f"  OBS pre-remap: {orig_id} -> {new_id}: {title_part}")

process_full("OBS", META["OBS"], OBS_KEYWORDS)

# ── IAC (0 files — full list, 50 keywords) ────────────────────────────────
IAC_KEYWORDS = [
    # L0
    ("IAC-001", None, "What Is Infrastructure as Code", "L0", "🌱"),
    ("IAC-002", None, "IaC vs Manual Infrastructure -- The Mental Model", "L0", "🌱"),
    ("IAC-003", None, "The IaC Ecosystem Map (Terraform, Pulumi, Ansible, CDK)", "L0", "🌱"),
    ("IAC-004", None, "Declarative vs Imperative IaC", "L0", "🌱"),
    ("IAC-005", None, "IaC in Production -- What to Expect", "L0", "🌱"),
    # L1
    ("IAC-006", None, "Terraform Basics (providers, resources, state)", "L1", "★☆☆"),
    ("IAC-007", None, "Terraform HCL Syntax", "L1", "★☆☆"),
    ("IAC-008", None, "Terraform State", "L1", "★☆☆"),
    ("IAC-009", None, "Terraform Plan and Apply", "L1", "★☆☆"),
    ("IAC-010", None, "Terraform Modules", "L1", "★☆☆"),
    ("IAC-011", None, "Terraform Variables and Outputs", "L1", "★☆☆"),
    ("IAC-012", None, "Terraform Providers", "L1", "★☆☆"),
    # L2
    ("IAC-013", None, "Terraform Remote State", "L2", "★★☆"),
    ("IAC-014", None, "Terraform Workspaces", "L2", "★★☆"),
    ("IAC-015", None, "Terraform Backends", "L2", "★★☆"),
    ("IAC-016", None, "Terraform Import", "L2", "★★☆"),
    ("IAC-017", None, "Ansible Basics (playbooks, inventory, roles)", "L2", "★★☆"),
    ("IAC-018", None, "AWS CDK (Cloud Development Kit)", "L2", "★★☆"),
    ("IAC-019", None, "Pulumi -- IaC with Real Languages", "L2", "★★☆"),
    ("IAC-020", None, "Helm -- Kubernetes Package Manager", "L2", "★★☆"),
    ("IAC-021", None, "GitOps Workflow for IaC", "L2", "★★☆"),
    # L3
    ("IAC-022", None, "Terraform State Locking and Drift Detection", "L3", "★★☆"),
    ("IAC-023", None, "Terraform Testing (Terratest, checkov)", "L3", "★★☆"),
    ("IAC-024", None, "Crossplane -- Kubernetes-Native IaC", "L3", "★★☆"),
    ("IAC-025", None, "Open Policy Agent (OPA) for IaC", "L3", "★★☆"),
    ("IAC-026", None, "IaC Security Scanning (tfsec, Bridgecrew)", "L3", "★★☆"),
    ("IAC-027", None, "Immutable Infrastructure Pattern", "L3", "★★☆"),
    ("IAC-028", None, "Idempotency in IaC", "L3", "★★☆"),
    ("IAC-029", None, "Secret Management in IaC", "L3", "★★☆"),
    ("IAC-030", None, "IaC Module Versioning Strategy", "L3", "★★☆"),
    ("IAC-031", None, "Packer -- Machine Image Building", "L3", "★★☆"),
    # L4
    ("IAC-032", None, "Terraform Provider Development", "L4", "★★★"),
    ("IAC-033", None, "Terraform Enterprise and Cloud (Remote Operations)", "L4", "★★★"),
    ("IAC-034", None, "Multi-Cloud IaC Strategy", "L4", "★★★"),
    ("IAC-035", None, "IaC at Enterprise Scale (Terragrunt, Atlantis)", "L4", "★★★"),
    ("IAC-036", None, "IaC Drift and Reconciliation Strategy", "L4", "★★★"),
    ("IAC-037", None, "IaC Compliance Enforcement", "L4", "★★★"),
    # L4.5
    ("IAC-038", None, "IaC Architecture Strategy", "L45", "🔥"),
    ("IAC-039", None, "Platform Engineering with IaC", "L45", "🔥"),
    ("IAC-040", None, "Golden Path Templates and Internal Developer Platform", "L45", "🔥"),
    ("IAC-041", None, "IaC Tool Selection Framework", "L45", "🔥"),
    # L5
    ("IAC-042", None, "IaC Abstraction Layer Design", "L5", "🔬"),
    ("IAC-043", None, "Desired State Convergence Theory", "L5", "🔬"),
    ("IAC-044", None, "IaC Language Design Research", "L5", "🔬"),
    # META
    ("IAC-045", None, "IaC Trade-off Framing", "META", "🧠"),
    ("IAC-046", None, "Infrastructure Automation Mental Model", "META", "🧠"),
    ("IAC-047", None, "Mutable vs Immutable Infrastructure Thinking", "META", "🧠"),
]
process_full("IAC", META["IAC"], IAC_KEYWORDS)

print("\nTier-6 done.")
