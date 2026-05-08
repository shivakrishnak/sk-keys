"""Tier-5: Distributed Architecture — DST, MSV, SYD, SAP, DPT"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tier_shift_lib import process_shift

BASE = pathlib.Path(r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture")

META = {
    "DST": dict(category="Distributed Systems", tier="tier-5-distributed-architecture",
                folder="DST-distributed-systems", parent="Distributed Systems",
                dir=BASE / "DST-distributed-systems"),
    "MSV": dict(category="Microservices", tier="tier-5-distributed-architecture",
                folder="MSV-microservices", parent="Microservices",
                dir=BASE / "MSV-microservices"),
    "SYD": dict(category="System Design", tier="tier-5-distributed-architecture",
                folder="SYD-system-design", parent="System Design",
                dir=BASE / "SYD-system-design"),
    "SAP": dict(category="Software Architecture Patterns", tier="tier-5-distributed-architecture",
                folder="SAP-software-architecture", parent="Software Architecture Patterns",
                dir=BASE / "SAP-software-architecture"),
    "DPT": dict(category="Design Patterns", tier="tier-5-distributed-architecture",
                folder="DPT-design-patterns", parent="Design Patterns",
                dir=BASE / "DPT-design-patterns"),
}

# ── DST (60 files → 006..065) ─────────────────────────────────────────────
process_shift("DST", META["DST"],
    l0_titles=[
        "What Is a Distributed System",
        "Why Distribution Is Hard",
        "The Distributed Systems Landscape -- A Map",
        "The Fallacies of Distributed Computing",
        "The Distributed Systems Ecosystem Map",
    ],
    l45_titles=[
        "Distributed System Architecture Strategy",
        "Consistency Model Selection Framework",
        "Failure Domain Design",
        "Distributed Tracing Architecture",
        "Global Distribution Strategy",
    ],
    l5_titles=[
        "Distributed Consensus Algorithm Design (Raft, Paxos)",
        "Distributed Transaction Theory",
        "Formal Models for Distributed Systems (TLA+)",
        "Research Frontiers in Distributed Systems",
    ],
    meta_titles=[
        "Failure-First Thinking",
        "Consistency Trade-off Framing",
        "Distribution Necessity Assessment",
    ],
)

# ── MSV (60 files → 006..065) ─────────────────────────────────────────────
process_shift("MSV", META["MSV"],
    l0_titles=[
        "What Are Microservices",
        "Monolith vs Microservices -- The Real Trade-off",
        "Why Microservices Became Popular",
        "The Microservices Ecosystem Map",
        "When NOT to Use Microservices",
    ],
    l45_titles=[
        "Service Decomposition Strategy",
        "Microservices Migration Strategy (Strangler Fig)",
        "Service Mesh Architecture Design",
        "Microservices Observability Architecture",
        "Event-Driven Microservices Design",
    ],
    l5_titles=[
        "Service Mesh Internals (Envoy, Istio)",
        "Service-to-Service Protocol Design",
        "Domain-Driven Decomposition Theory",
        "Microservices Research and Anti-Patterns",
    ],
    meta_titles=[
        "Decomposition Trade-off Framing",
        "Microservices Necessity Assessment",
        "Service Boundary Mental Model",
    ],
)

# ── SYD (45 files → 006..050) ─────────────────────────────────────────────
process_shift("SYD", META["SYD"],
    l0_titles=[
        "What Is System Design",
        "The System Design Interview Mental Model",
        "How to Approach Any System Design Problem",
        "Estimation and Back-of-Envelope Thinking",
        "The System Design Ecosystem Map",
    ],
    l45_titles=[
        "System Design at Hyperscale",
        "Multi-Region Architecture Strategy",
        "Cost-Performance Trade-off Architecture",
        "System Evolution Strategy",
        "Platform Architecture Design",
    ],
    l5_titles=[
        "Emergent Architecture Patterns",
        "Theoretical Foundations of Scalable Systems",
        "Formal Capacity Planning Models",
        "System Design Research and Case Studies",
    ],
    meta_titles=[
        "Constraint-First System Design Thinking",
        "Scale Estimation Mental Model",
        "Trade-off Navigation Framework",
    ],
)

# ── SAP (47 files → 006..052) ─────────────────────────────────────────────
process_shift("SAP", META["SAP"],
    l0_titles=[
        "What Is Software Architecture",
        "Why Architecture Decisions Matter",
        "The Architecture Landscape -- Styles and Patterns",
        "Architecture vs Design vs Implementation",
        "The Software Architecture Ecosystem Map",
    ],
    l45_titles=[
        "Architecture Decision Records (ADR) Strategy",
        "Architecture Review Process Design",
        "Legacy Modernization Strategy",
        "Architecture Fitness Functions",
        "Architecture Governance at Scale",
    ],
    l5_titles=[
        "Formal Architecture Specification (C4, ADL, UML)",
        "Architecture Theory and Research",
        "Software Architecture Pattern Research",
        "Evolutionary Architecture Design",
    ],
    meta_titles=[
        "Architecture Trade-off Framing",
        "Architecture Necessity Assessment",
        "Technical Debt Mental Model",
    ],
)

# ── DPT (55 files → 006..060) ─────────────────────────────────────────────
process_shift("DPT", META["DPT"],
    l0_titles=[
        "What Are Design Patterns and Why They Exist",
        "The Gang of Four -- Origin and Philosophy",
        "Pattern vs Anti-Pattern vs Idiom",
        "How to Recognize When a Pattern Applies",
        "The Design Patterns Ecosystem Map",
    ],
    l45_titles=[
        "Pattern Selection Framework",
        "Pattern Evolution in Modern Languages",
        "Anti-Pattern Recognition and Refactoring",
        "Pattern-Driven Architecture Design",
        "Patterns in Distributed Systems",
    ],
    l5_titles=[
        "Pattern Language Theory (Christopher Alexander)",
        "Formal Pattern Specification",
        "Pattern Mining and Discovery Research",
        "Meta-Pattern Design",
    ],
    meta_titles=[
        "Pattern-Recognition Mental Model",
        "Pattern Trade-off Framing",
        "Over-Engineering Risk Thinking",
    ],
)

print("\nTier-5 done.")
