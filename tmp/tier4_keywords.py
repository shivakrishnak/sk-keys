"""Tier-4: Data — DBF, NDB, CCH, DAT, BIG"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tier_shift_lib import process_shift

BASE = pathlib.Path(r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-4-data")

META = {
    "DBF": dict(category="Database Fundamentals", tier="tier-4-data",
                folder="DBF-database-fundamentals", parent="Database Fundamentals",
                dir=BASE / "DBF-database-fundamentals"),
    "NDB": dict(category="NoSQL & Distributed Databases", tier="tier-4-data",
                folder="NDB-nosql-distributed", parent="NoSQL & Distributed Databases",
                dir=BASE / "NDB-nosql-distributed"),
    "CCH": dict(category="Caching", tier="tier-4-data",
                folder="CCH-caching", parent="Caching",
                dir=BASE / "CCH-caching"),
    "DAT": dict(category="Data Fundamentals", tier="tier-4-data",
                folder="DAT-data-fundamentals", parent="Data Fundamentals",
                dir=BASE / "DAT-data-fundamentals"),
    "BIG": dict(category="Big Data & Streaming", tier="tier-4-data",
                folder="BIG-bigdata-streaming", parent="Big Data & Streaming",
                dir=BASE / "BIG-bigdata-streaming"),
}

# ── DBF (50 files → 006..055) ─────────────────────────────────────────────
process_shift("DBF", META["DBF"],
    l0_titles=[
        "What Is a Database and Why It Exists",
        "The Database Landscape -- A Map",
        "How Data Gets Stored and Retrieved",
        "RDBMS vs NoSQL -- When to Choose",
        "The SQL Ecosystem Map",
    ],
    l45_titles=[
        "Database Selection Framework",
        "Database Architecture at Scale",
        "Multi-Database Strategy (Polyglot Persistence)",
        "Database Migration Strategy",
        "Database Observability Strategy",
    ],
    l5_titles=[
        "RDBMS Engine Internals (InnoDB, PostgreSQL)",
        "Transaction Protocol Design (2PC, MVCC)",
        "Query Optimizer Design",
        "Storage Engine Architecture",
    ],
    meta_titles=[
        "ACID Trade-off Framing",
        "Database Selection Mental Model",
        "Query Performance Intuition",
    ],
)

# ── NDB (36 files → 006..041) ─────────────────────────────────────────────
process_shift("NDB", META["NDB"],
    l0_titles=[
        "Why NoSQL Was Invented",
        "The NoSQL Landscape -- A Map",
        "SQL vs NoSQL -- When to Choose What",
        "The CAP Theorem in Plain English",
        "NoSQL in Production -- What to Expect",
    ],
    l45_titles=[
        "Multi-Model Database Strategy",
        "NoSQL Migration Strategy (SQL to NoSQL)",
        "Global Distribution Database Design",
        "Event Store Architecture",
        "NoSQL Selection Framework",
    ],
    l5_titles=[
        "Distributed Database Internals (Consensus, Paxos)",
        "Multi-Version Concurrency Control at Scale",
        "Global Distributed Transactions Research",
        "NoSQL Engine Architecture",
    ],
    meta_titles=[
        "Consistency Trade-off Framing",
        "NoSQL Selection Mental Model",
        "Distributed State Design Thinking",
    ],
)

# ── CCH (20 files → 006..025) ─────────────────────────────────────────────
process_shift("CCH", META["CCH"],
    l0_titles=[
        "Why Caching Exists -- The Performance Problem",
        "The Caching Landscape -- A Map",
        "Cache Anatomy (Hit, Miss, Eviction)",
        "When NOT to Cache",
        "The Cache Ecosystem Map (Redis, Memcached, CDN)",
    ],
    l45_titles=[
        "Caching Architecture Strategy",
        "Cache Invalidation Architecture",
        "Distributed Cache Design",
        "Cache-Aside vs Write-Through at Scale",
        "Multi-Level Caching Strategy",
    ],
    l5_titles=[
        "Cache Coherence Protocol Design",
        "Distributed Cache Algorithm Research",
        "Cache Replacement Policy Design",
        "Consistent Hashing in Cache Systems",
    ],
    meta_titles=[
        "Cache Trade-off Framing",
        "Invalidation Problem Mental Model",
        "Cache Selection Framework",
    ],
)

# ── DAT (37 files → 006..042) ─────────────────────────────────────────────
process_shift("DAT", META["DAT"],
    l0_titles=[
        "What Is Data Engineering",
        "The Data Ecosystem -- A Map",
        "Data vs Information vs Knowledge",
        "Structured vs Unstructured vs Semi-Structured Data",
        "The Modern Data Stack Map",
    ],
    l45_titles=[
        "Data Architecture Strategy (Lake vs Warehouse vs Mesh)",
        "Data Quality at Scale",
        "Data Governance Framework Design",
        "Data Platform Architecture",
        "Data Contract Strategy",
    ],
    l5_titles=[
        "Data System Internals (Parquet, Arrow, Iceberg)",
        "Data Model Theory",
        "Distributed Data Processing Design",
        "Data Lineage System Architecture",
    ],
    meta_titles=[
        "Data Trade-off Framing",
        "Data Modeling Mental Model",
        "Data Platform Selection Framework",
    ],
)

# ── BIG (40 files → 006..045) ─────────────────────────────────────────────
process_shift("BIG", META["BIG"],
    l0_titles=[
        "What Is Big Data -- The 3Vs Problem",
        "The Streaming vs Batch Divide",
        "The Big Data Ecosystem Map (Hadoop, Spark, Kafka)",
        "Why Distributed Processing Matters",
        "Big Data in Production -- What to Expect",
    ],
    l45_titles=[
        "Streaming Architecture Design",
        "Lambda Architecture vs Kappa Architecture Trade-offs",
        "Real-Time Analytics Platform Design",
        "Event-Driven Architecture Strategy",
        "Big Data Platform Selection Framework",
    ],
    l5_titles=[
        "Distributed Stream Processing Internals",
        "Consensus in Distributed Streaming Systems",
        "State Management in Streaming Pipelines",
        "Fault Tolerance in Distributed Pipelines",
    ],
    meta_titles=[
        "Batch vs Stream Trade-off Framing",
        "Big Data System Selection Mental Model",
        "Data Pipeline Design Thinking",
    ],
)

print("\nTier-4 done.")
