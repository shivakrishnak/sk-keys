"""Tier-3: Java & JVM — JVM, JLG, JCC, SPR"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tier_shift_lib import process_shift, process_full

BASE = pathlib.Path(r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-3-java")

META = {
    "JVM": dict(category="Java & JVM Internals", tier="tier-3-java",
                folder="JVM-java-jvm-internals", parent="Java & JVM Internals",
                dir=BASE / "JVM-java-jvm-internals"),
    "JLG": dict(category="Java Language", tier="tier-3-java",
                folder="JLG-java-language", parent="Java Language",
                dir=BASE / "JLG-java-language"),
    "JCC": dict(category="Java Concurrency", tier="tier-3-java",
                folder="JCC-java-concurrency", parent="Java Concurrency",
                dir=BASE / "JCC-java-concurrency"),
    "SPR": dict(category="Spring Core", tier="tier-3-java",
                folder="SPR-spring-core", parent="Spring Core",
                dir=BASE / "SPR-spring-core"),
}

# ── JVM ──────────────────────────────────────────────────────────────────────
# 51 files; JVM-001 (G1GC) is duplicate of JVM-030 (G1GC) → retire JVM-001
# Kept 50 → 006..055; L4.5 056..060; L5 061..064; META 065..067 → total 67
process_shift("JVM", META["JVM"],
    retire_ids={"JVM-001"},
    l0_titles=[
        "What Is the JVM — A Mental Model",
        "Why the JVM Was Invented",
        "JVM vs JRE vs JDK",
        "How Java Code Runs — Bytecode to Execution",
        "The JVM Ecosystem Map (OpenJDK, GraalVM, Languages)",
    ],
    l45_titles=[
        "GC Tuning Strategy for Production JVMs",
        "JVM Architecture Decisions at Scale",
        "JVM Selection Framework (HotSpot vs GraalVM)",
        "Heap Sizing and Memory Planning Strategy",
        "JVM Observability Strategy",
    ],
    l5_titles=[
        "JVM Specification Deep Dive",
        "GC Algorithm Design Principles",
        "JIT Compilation Research (Truffle, Graal IR)",
        "JVM Language Design (Bytecode Targeting)",
    ],
    meta_titles=[
        "JVM-First Debugging Mental Model",
        "Performance Intuition via JVM Internals",
        "GC Trade-off Framing",
    ],
)

# ── JLG ──────────────────────────────────────────────────────────────────────
# 35 files JLG-001..035 → 006..040; L4.5 041..045; L5 046..049; META 050..052 → 52
process_shift("JLG", META["JLG"],
    l0_titles=[
        "What Is Java — History and Philosophy",
        "The Java Ecosystem Map (SE, EE, ME, Android)",
        "Why Java Is Still Dominant",
        "Java vs Other JVM Languages (Kotlin, Scala, Groovy)",
        "Java Versioning and LTS Release Strategy",
    ],
    l45_titles=[
        "Java Version Migration Strategy (8 → 17 → 21)",
        "Java API Design at Scale",
        "Java Modularity Strategy (JPMS)",
        "Java Performance Profiling at Scale",
        "Java in Polyglot Architecture",
    ],
    l5_titles=[
        "Java Language Specification Deep Dive",
        "Project Valhalla — Value Types and Primitives",
        "Project Panama — Foreign Function and Memory API",
        "Java Language Design History and Rationale",
    ],
    meta_titles=[
        "Java API Design Thinking",
        "Language Feature Trade-off Framing",
        "Java Ecosystem Selection Framework",
    ],
)

# ── JCC ──────────────────────────────────────────────────────────────────────
# 49 files; JCC-001..009 are duplicates of JCC-037..047 → retire 001..009
# Kept 40 (010..049) → 006..045; L4.5 046..050; L5 051..054; META 055..057 → 57
process_shift("JCC", META["JCC"],
    retire_ids={"JCC-001","JCC-002","JCC-003","JCC-004","JCC-005",
                "JCC-006","JCC-007","JCC-008","JCC-009"},
    l0_titles=[
        "Why Concurrency Is Hard",
        "The Thread Safety Problem — A Mental Model",
        "Java's Concurrency Approach — History and Philosophy",
        "Concurrency vs Parallelism in Java",
        "The Java Concurrency Ecosystem Map",
    ],
    l45_titles=[
        "Concurrency Architecture Patterns in Java",
        "Virtual Thread Migration Strategy (Loom)",
        "Concurrent System Design at Scale",
        "Lock-Free Algorithm Strategy",
        "Thread Model Selection Framework",
    ],
    l5_titles=[
        "Java Memory Model Specification Deep Dive",
        "Lock-Free Data Structure Design",
        "Concurrent Algorithm Research",
        "Structured Concurrency Design Principles",
    ],
    meta_titles=[
        "Concurrency-First Thinking",
        "Shared State Risk Intuition",
        "Thread Safety Trade-off Framing",
    ],
)

# ── SPR ──────────────────────────────────────────────────────────────────────
# 53 files SPR-001..053 → 006..058; L4.5 059..063; L5 064..067; META 068..070 → 70
process_shift("SPR", META["SPR"],
    l0_titles=[
        "What Is Spring — History and Philosophy",
        "The Spring Ecosystem Map",
        "Why Spring Boot Changed Java Development",
        "Spring vs Jakarta EE vs Micronaut vs Quarkus",
        "Spring in Production — What to Expect",
    ],
    l45_titles=[
        "Spring Architecture at Scale",
        "Spring Migration Strategy (MVC → WebFlux)",
        "Spring Boot Configuration Strategy",
        "Spring Security Architecture Design",
        "Microservice Decomposition with Spring Cloud",
    ],
    l5_titles=[
        "Spring Framework Internals Deep Dive",
        "Spring Reactive Model (Project Reactor Internals)",
        "Spring Native and GraalVM Integration",
        "Spring Specification and Extension Points",
    ],
    meta_titles=[
        "IoC-First Thinking",
        "Spring Configuration Trade-off Framing",
        "Framework Selection Mental Model",
    ],
)

print("\nTier-3 done.")
