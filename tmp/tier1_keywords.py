"""
Tier-1 Gap Analysis + Keyword Master List Generator
For all 4 categories: CSF, DSA, LNX, OSY

Each keyword has:
  - new_id: the ID in the new ordered list (L0 first, then L1, ..., META last)
  - old_id: None if new keyword (gap), else the original ID
  - title: keyword title
  - level: L0/L1/L2/L3/L4/L45/L5/META
  - difficulty: star rating
  - status: 'existing' or 'new'

Files are renamed from old filename → new filename.
New keywords get placeholder .md files created.
"""

import pathlib, shutil, re

BASE = pathlib.Path(r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-1-foundations")

# ─────────────────────────────────────────────────────────────────────────────
# MASTER KEYWORD LISTS  (sorted L0 → META within each category)
# Format: (new_id, old_id_or_None, title, level, difficulty)
# ─────────────────────────────────────────────────────────────────────────────

CSF_KEYWORDS = [
    # L0 — ORIENTATION (new)
    ("CSF-001", None, "What Is Computer Science — A Map",              "L0", "🌱"),
    ("CSF-002", None, "Why Programming Paradigms Exist",               "L0", "🌱"),
    ("CSF-003", None, "The History of Programming Languages",          "L0", "🌱"),
    ("CSF-004", None, "How Code Becomes Execution — Big Picture",      "L0", "🌱"),
    ("CSF-005", None, "The CS Ecosystem Map (Languages, Runtimes, OS)","L0", "🌱"),

    # L1 — FOUNDATIONAL (existing CSF-001..010 shift here)
    ("CSF-006", "CSF-001", "Imperative Programming",                   "L1", "★☆☆"),
    ("CSF-007", "CSF-002", "Declarative Programming",                  "L1", "★☆☆"),
    ("CSF-008", "CSF-005", "Procedural Programming",                   "L1", "★☆☆"),
    ("CSF-009", "CSF-003", "Object-Oriented Programming (OOP)",        "L1", "★☆☆"),
    ("CSF-010", "CSF-004", "Functional Programming",                   "L1", "★☆☆"),
    ("CSF-011", "CSF-006", "Event-Driven Programming",                 "L1", "★☆☆"),
    ("CSF-012", "CSF-010", "Type Systems (Static vs Dynamic)",         "L1", "★☆☆"),
    ("CSF-013", "CSF-011", "Strong vs Weak Typing",                    "L1", "★☆☆"),
    ("CSF-014", "CSF-012", "Compiled vs Interpreted Languages",        "L1", "★☆☆"),
    ("CSF-015", "CSF-013", "Memory Management Models",                 "L1", "★☆☆"),
    ("CSF-016", "CSF-016", "Abstraction",                              "L1", "★☆☆"),
    ("CSF-017", "CSF-015", "Synchronous vs Asynchronous",              "L1", "★☆☆"),
    ("CSF-018", "CSF-014", "Concurrency vs Parallelism",               "L1", "★☆☆"),
    ("CSF-019", None,       "Variables, Types, and Scope",             "L1", "★☆☆"),
    ("CSF-020", None,       "Control Flow (if, loops, switch)",        "L1", "★☆☆"),
    ("CSF-021", None,       "Functions and Procedures",                "L1", "★☆☆"),
    ("CSF-022", None,       "Error vs Exception",                      "L1", "★☆☆"),
    ("CSF-023", None,       "Stack vs Heap Memory",                    "L1", "★☆☆"),

    # L2 — WORKING
    ("CSF-024", "CSF-017", "Encapsulation",                            "L2", "★★☆"),
    ("CSF-025", "CSF-018", "Polymorphism",                             "L2", "★★☆"),
    ("CSF-026", "CSF-019", "Inheritance",                              "L2", "★★☆"),
    ("CSF-027", "CSF-020", "Composition over Inheritance",             "L2", "★★☆"),
    ("CSF-028", "CSF-021", "Recursion",                                "L2", "★★☆"),
    ("CSF-029", "CSF-026", "First-Class Functions",                    "L2", "★★☆"),
    ("CSF-030", "CSF-027", "Higher-Order Functions",                   "L2", "★★☆"),
    ("CSF-031", "CSF-028", "Side Effects",                             "L2", "★★☆"),
    ("CSF-032", "CSF-030", "Idempotency",                              "L2", "★★☆"),
    ("CSF-033", None,       "Closures",                                "L2", "★★☆"),
    ("CSF-034", None,       "Immutability",                            "L2", "★★☆"),
    ("CSF-035", None,       "Null Safety and Null Anti-Pattern",       "L2", "★★☆"),
    ("CSF-036", None,       "Exception Handling Patterns",             "L2", "★★☆"),
    ("CSF-037", None,       "Modules and Packages",                    "L2", "★★☆"),
    ("CSF-038", None,       "Interfaces vs Abstract Classes",          "L2", "★★☆"),
    ("CSF-039", None,       "Generics and Parametric Polymorphism",    "L2", "★★☆"),
    ("CSF-040", None,       "Pattern Matching",                        "L2", "★★☆"),

    # L3 — INTERMEDIATE
    ("CSF-041", "CSF-007", "Reactive Programming",                     "L3", "★★☆"),
    ("CSF-042", "CSF-008", "Aspect-Oriented Programming",              "L3", "★★☆"),
    ("CSF-043", "CSF-009", "Metaprogramming",                          "L3", "★★☆"),
    ("CSF-044", "CSF-022", "Tail Recursion",                           "L3", "★★☆"),
    ("CSF-045", "CSF-029", "Referential Transparency",                 "L3", "★★☆"),
    ("CSF-046", None,       "Algebraic Data Types (ADTs)",             "L3", "★★☆"),
    ("CSF-047", None,       "Monads and Functors",                     "L3", "★★☆"),
    ("CSF-048", None,       "Continuation-Passing Style (CPS)",        "L3", "★★☆"),
    ("CSF-049", None,       "Memory Leak Detection and Tooling",       "L3", "★★☆"),
    ("CSF-050", None,       "Garbage Collection Algorithms Overview",  "L3", "★★☆"),
    ("CSF-051", None,       "Type Inference",                          "L3", "★★☆"),
    ("CSF-052", None,       "Structural vs Nominal Typing",            "L3", "★★☆"),
    ("CSF-053", None,       "Concurrency Anti-Patterns (Shared State)","L3", "★★☆"),
    ("CSF-054", None,       "Testing Paradigms for CS Concepts",       "L3", "★★☆"),
    ("CSF-055", None,       "Language Performance Trade-offs",         "L3", "★★☆"),

    # L4 — EXPERT
    ("CSF-056", "CSF-023", "Turing Completeness",                      "L4", "★★★"),
    ("CSF-057", None,       "Memory Safety Vulnerabilities in Lang Design","L4","★★★"),
    ("CSF-058", None,       "JIT vs AOT Compilation Deep Dive",        "L4", "★★★"),
    ("CSF-059", None,       "GC Pause Analysis and Production Impact", "L4", "★★★"),
    ("CSF-060", None,       "Concurrency Models Compared (Actor, CSP, STM)","L4","★★★"),
    ("CSF-061", None,       "Undefined Behaviour in Language Specs",   "L4", "★★★"),
    ("CSF-062", None,       "Language Runtime Internals",              "L4", "★★★"),
    ("CSF-063", None,       "Therac-25 Incident (1985) — Software Fails","L4","★★★"),
    ("CSF-064", None,       "Ariane 5 Overflow Bug (1996)",            "L4", "★★★"),
    ("CSF-065", None,       "Dependency Hell and Package Management",  "L4", "★★★"),

    # L4.5 — ARCHITECT
    ("CSF-066", None,       "Polyglot Architecture Strategy",          "L45","🔥"),
    ("CSF-067", None,       "Language Evaluation Framework",           "L45","🔥"),
    ("CSF-068", None,       "Paradigm Migration Strategy (OOP → FP)",  "L45","🔥"),
    ("CSF-069", None,       "Type System Design for Large Codebases",  "L45","🔥"),
    ("CSF-070", None,       "Compiler/Runtime Selection at Scale",     "L45","🔥"),

    # L5 — CREATOR
    ("CSF-071", "CSF-024", "Church-Turing Thesis",                     "L5", "🔬"),
    ("CSF-072", "CSF-025", "Lambda Calculus",                          "L5", "🔬"),
    ("CSF-073", None,       "Curry-Howard Correspondence",             "L5", "🔬"),
    ("CSF-074", None,       "Category Theory for Programmers",         "L5", "🔬"),
    ("CSF-075", None,       "Formal Semantics (Denotational, Operational)","L5","🔬"),
    ("CSF-076", None,       "Type Theory (System F, HM Inference)",    "L5", "🔬"),
    ("CSF-077", None,       "Language Design Rationale (Rust, Go, Kotlin)","L5","🔬"),

    # META — META-SKILLS
    ("CSF-078", None,       "Paradigm-Agnostic Thinking",              "META","🧠"),
    ("CSF-079", None,       "Trade-off Framing (Any Language Choice)", "META","🧠"),
    ("CSF-080", None,       "First-Principles Language Selection",     "META","🧠"),
]

DSA_KEYWORDS = [
    # L0 — ORIENTATION (new)
    ("DSA-001", None, "Why Data Structures and Algorithms Matter",     "L0", "🌱"),
    ("DSA-002", None, "The Problem of Efficiency",                     "L0", "🌱"),
    ("DSA-003", None, "DSA in Real Systems — Where They Appear",       "L0", "🌱"),
    ("DSA-004", None, "How to Think About Problems Algorithmically",   "L0", "🌱"),
    ("DSA-005", None, "The DSA Ecosystem Map (LeetCode, Competitions)","L0", "🌱"),

    # L1 — FOUNDATIONAL
    ("DSA-006", "DSA-018", "Time Complexity Big-O",                    "L1", "★☆☆"),
    ("DSA-007", "DSA-019", "Space Complexity",                         "L1", "★☆☆"),
    ("DSA-008", "DSA-001", "Array",                                    "L1", "★☆☆"),
    ("DSA-009", "DSA-002", "LinkedList",                               "L1", "★☆☆"),
    ("DSA-010", "DSA-003", "Stack",                                    "L1", "★☆☆"),
    ("DSA-011", "DSA-004", "Queue Deque",                              "L1", "★☆☆"),
    ("DSA-012", "DSA-005", "HashMap",                                  "L1", "★☆☆"),
    ("DSA-013", "DSA-010", "Graph",                                    "L1", "★☆☆"),
    ("DSA-014", None,       "Tree (Binary Tree Basics)",               "L1", "★☆☆"),
    ("DSA-015", None,       "Recursion and Base Cases",                "L1", "★☆☆"),
    ("DSA-016", None,       "Iteration vs Recursion",                  "L1", "★☆☆"),
    ("DSA-017", None,       "Sorting — Why It Matters",                "L1", "★☆☆"),
    ("DSA-018", None,       "Searching — Linear vs Binary",            "L1", "★☆☆"),

    # L2 — WORKING
    ("DSA-019", "DSA-006", "TreeMap",                                  "L2", "★★☆"),
    ("DSA-020", "DSA-007", "Heap (Min-Max)",                           "L2", "★★☆"),
    ("DSA-021", "DSA-008", "Priority Queue",                           "L2", "★★☆"),
    ("DSA-022", "DSA-009", "Trie",                                     "L2", "★★☆"),
    ("DSA-023", "DSA-016", "LRU Cache",                                "L2", "★★☆"),
    ("DSA-024", "DSA-041", "Binary Search",                            "L2", "★★☆"),
    ("DSA-025", "DSA-034", "Quicksort",                                "L2", "★★☆"),
    ("DSA-026", "DSA-035", "Mergesort",                                "L2", "★★☆"),
    ("DSA-027", "DSA-026", "BFS",                                      "L2", "★★☆"),
    ("DSA-028", "DSA-027", "DFS",                                      "L2", "★★☆"),
    ("DSA-029", "DSA-039", "Two Pointer",                              "L2", "★★☆"),
    ("DSA-030", "DSA-040", "Sliding Window",                           "L2", "★★☆"),
    ("DSA-031", "DSA-021", "Memoization",                              "L2", "★★☆"),
    ("DSA-032", "DSA-043", "Bit Manipulation",                         "L2", "★★☆"),
    ("DSA-033", "DSA-061", "Prefix Sum and Difference Array",          "L2", "★★☆"),
    ("DSA-034", None,       "Common Coding Anti-Patterns",             "L2", "★★☆"),

    # L3 — INTERMEDIATE
    ("DSA-035", "DSA-020", "Amortized Analysis",                       "L3", "★★☆"),
    ("DSA-036", "DSA-023", "Divide and Conquer",                       "L3", "★★☆"),
    ("DSA-037", "DSA-024", "Greedy Algorithm",                         "L3", "★★☆"),
    ("DSA-038", "DSA-025", "Dynamic Programming",                      "L3", "★★☆"),
    ("DSA-039", "DSA-022", "Tabulation (Bottom-Up DP)",                "L3", "★★☆"),
    ("DSA-040", "DSA-042", "Backtracking",                             "L3", "★★☆"),
    ("DSA-041", "DSA-028", "Topological Sort",                         "L3", "★★☆"),
    ("DSA-042", "DSA-029", "Dijkstra",                                 "L3", "★★☆"),
    ("DSA-043", "DSA-032", "Union-Find (Disjoint Set)",                "L3", "★★☆"),
    ("DSA-044", "DSA-036", "Timsort",                                  "L3", "★★☆"),
    ("DSA-045", "DSA-037", "Heapsort",                                 "L3", "★★☆"),
    ("DSA-046", "DSA-038", "Radix Sort",                               "L3", "★★☆"),
    ("DSA-047", "DSA-044", "String Matching (KMP, Rabin-Karp)",        "L3", "★★☆"),
    ("DSA-048", "DSA-045", "Hashing Techniques",                       "L3", "★★☆"),
    ("DSA-049", "DSA-049", "Longest Common Subsequence",               "L3", "★★☆"),
    ("DSA-050", "DSA-050", "Knapsack Problem",                         "L3", "★★☆"),
    ("DSA-051", "DSA-058", "Sorting Stability",                        "L3", "★★☆"),
    ("DSA-052", "DSA-054", "Space-Time Trade-off",                     "L3", "★★☆"),
    ("DSA-053", "DSA-060", "Recursion vs Iteration Trade-offs",        "L3", "★★☆"),
    ("DSA-054", "DSA-059", "In-Place vs Out-of-Place",                 "L3", "★★☆"),
    ("DSA-055", None,       "Algorithm Complexity Profiling Tools",    "L3", "★★☆"),
    ("DSA-056", None,       "Cache-Friendly Data Structures",          "L3", "★★☆"),

    # L4 — EXPERT
    ("DSA-057", "DSA-011", "Segment Tree",                             "L4", "★★★"),
    ("DSA-058", "DSA-012", "Fenwick Tree (BIT)",                       "L4", "★★★"),
    ("DSA-059", "DSA-013", "Skip List",                                "L4", "★★★"),
    ("DSA-060", "DSA-014", "Bloom Filter",                             "L4", "★★★"),
    ("DSA-061", "DSA-015", "Consistent Hash Ring",                     "L4", "★★★"),
    ("DSA-062", "DSA-017", "LFU Cache",                                "L4", "★★★"),
    ("DSA-063", "DSA-030", "Bellman-Ford",                             "L4", "★★★"),
    ("DSA-064", "DSA-031", "A-Star Search",                            "L4", "★★★"),
    ("DSA-065", "DSA-033", "Kruskal Prim",                             "L4", "★★★"),
    ("DSA-066", "DSA-046", "Graph Coloring",                           "L4", "★★★"),
    ("DSA-067", "DSA-047", "Minimum Spanning Tree",                    "L4", "★★★"),
    ("DSA-068", "DSA-048", "Strongly Connected Components",            "L4", "★★★"),
    ("DSA-069", "DSA-051", "NP-Complete Problems",                     "L4", "★★★"),
    ("DSA-070", "DSA-052", "P vs NP",                                  "L4", "★★★"),
    ("DSA-071", "DSA-053", "Complexity Classes",                       "L4", "★★★"),
    ("DSA-072", "DSA-055", "Randomized Algorithms",                    "L4", "★★★"),
    ("DSA-073", None,       "B-Tree and B+ Tree",                      "L4", "★★★"),
    ("DSA-074", None,       "Algorithm Correctness and Loop Invariants","L4","★★★"),
    ("DSA-075", None,       "Memory Hierarchy Impact on Algorithm Choice","L4","★★★"),

    # L4.5 — ARCHITECT
    ("DSA-076", None,       "Choosing Data Structures at System Scale","L45","🔥"),
    ("DSA-077", None,       "Algorithm Selection Framework",           "L45","🔥"),
    ("DSA-078", None,       "Distributed DSA — Consistent Hashing at Scale","L45","🔥"),
    ("DSA-079", None,       "Trade-off Navigation: Latency vs Correctness","L45","🔥"),

    # L5 — CREATOR
    ("DSA-080", "DSA-056", "Approximation Algorithms",                 "L5", "🔬"),
    ("DSA-081", "DSA-057", "Monte Carlo vs Las Vegas Algorithms",      "L5", "🔬"),
    ("DSA-082", None,       "Information-Theoretic Complexity Bounds", "L5", "🔬"),
    ("DSA-083", None,       "Streaming Algorithms and Sketches",       "L5", "🔬"),
    ("DSA-084", None,       "Algorithm Design Paradigm Research",      "L5", "🔬"),

    # META
    ("DSA-085", None,       "Recognising Problem Class on Sight",      "META","🧠"),
    ("DSA-086", None,       "Trade-off Reasoning for Any DS Choice",   "META","🧠"),
    ("DSA-087", None,       "Back-of-Envelope Complexity Estimation",  "META","🧠"),
]

LNX_KEYWORDS = [
    # L0 — ORIENTATION (new)
    ("LNX-001", None, "What Is Linux and Why It Powers the World",     "L0", "🌱"),
    ("LNX-002", None, "The Linux Kernel — A Simple Mental Model",      "L0", "🌱"),
    ("LNX-003", None, "Linux Distributions — The Ecosystem Map",       "L0", "🌱"),
    ("LNX-004", None, "Why Engineers Learn Linux",                     "L0", "🌱"),
    ("LNX-005", None, "Open Source and the GNU Philosophy",            "L0", "🌱"),

    # L1 — FOUNDATIONAL
    ("LNX-006", "LNX-001", "Linux File System Hierarchy",              "L1", "★☆☆"),
    ("LNX-007", "LNX-002", "File Permissions (chmod, chown)",          "L1", "★☆☆"),
    ("LNX-008", "LNX-003", "Users and Groups",                         "L1", "★☆☆"),
    ("LNX-009", "LNX-004", "Shell (bash, zsh)",                        "L1", "★☆☆"),
    ("LNX-010", "LNX-006", "stdin / stdout / stderr",                  "L1", "★☆☆"),
    ("LNX-011", "LNX-007", "Pipes and Redirection",                    "L1", "★☆☆"),
    ("LNX-012", "LNX-008", "Process Management (ps, top, kill)",       "L1", "★☆☆"),
    ("LNX-013", "LNX-011", "Environment Variables",                    "L1", "★☆☆"),
    ("LNX-014", "LNX-012", "Package Managers (apt, yum, dnf)",         "L1", "★☆☆"),
    ("LNX-015", "LNX-013", "SSH",                                      "L1", "★☆☆"),
    ("LNX-016", "LNX-019", "Symbolic Links and Hard Links",            "L1", "★☆☆"),
    ("LNX-017", None,       "Basic Text Editors (vim, nano)",          "L1", "★☆☆"),
    ("LNX-018", None,       "File Operations (cp, mv, rm, mkdir)",     "L1", "★☆☆"),

    # L2 — WORKING
    ("LNX-019", "LNX-005", "Shell Scripting",                          "L2", "★★☆"),
    ("LNX-020", "LNX-010", "Cron Jobs",                                "L2", "★★☆"),
    ("LNX-021", "LNX-014", "SCP / rsync",                              "L2", "★★☆"),
    ("LNX-022", "LNX-015", "curl / wget",                              "L2", "★★☆"),
    ("LNX-023", "LNX-016", "grep / awk / sed",                         "L2", "★★☆"),
    ("LNX-024", "LNX-017", "find / xargs",                             "L2", "★★☆"),
    ("LNX-025", "LNX-018", "tar / gzip / zip",                         "L2", "★★☆"),
    ("LNX-026", "LNX-022", "Linux Networking (ip, ss, netstat)",       "L2", "★★☆"),
    ("LNX-027", "LNX-009", "Systemd / Init System",                    "L2", "★★☆"),
    ("LNX-028", "LNX-039", "tmux / screen",                            "L2", "★★☆"),
    ("LNX-029", None,       "Log Management (journalctl, syslog)",     "L2", "★★☆"),
    ("LNX-030", None,       "Shell Scripting Anti-Patterns",           "L2", "★★☆"),
    ("LNX-031", None,       "User Permission Anti-Pattern (run as root)","L2","★★☆"),

    # L3 — INTERMEDIATE
    ("LNX-032", "LNX-020", "/proc File System",                        "L3", "★★☆"),
    ("LNX-033", "LNX-021", "/sys File System",                         "L3", "★★☆"),
    ("LNX-034", "LNX-023", "iptables / nftables",                      "L3", "★★☆"),
    ("LNX-035", "LNX-024", "tcpdump / Wireshark",                      "L3", "★★☆"),
    ("LNX-036", "LNX-025", "strace / ltrace",                          "L3", "★★☆"),
    ("LNX-037", "LNX-026", "lsof",                                     "L3", "★★☆"),
    ("LNX-038", "LNX-027", "ulimit",                                   "L3", "★★☆"),
    ("LNX-039", "LNX-028", "swap Management",                          "L3", "★★☆"),
    ("LNX-040", "LNX-029", "Memory (free, vmstat)",                    "L3", "★★☆"),
    ("LNX-041", "LNX-030", "Disk I/O (iostat, iotop)",                 "L3", "★★☆"),
    ("LNX-042", "LNX-031", "Kernel Modules",                           "L3", "★★☆"),
    ("LNX-043", "LNX-038", "/etc/hosts / DNS Resolution",              "L3", "★★☆"),
    ("LNX-044", None,       "System Call Tracing and Analysis",        "L3", "★★☆"),
    ("LNX-045", None,       "Linux Performance Profiling Tools",       "L3", "★★☆"),
    ("LNX-046", None,       "Service Security Hardening Basics",       "L3", "★★☆"),

    # L4 — EXPERT
    ("LNX-047", "LNX-032", "Linux Namespaces",                         "L4", "★★★"),
    ("LNX-048", "LNX-033", "Cgroups",                                  "L4", "★★★"),
    ("LNX-049", "LNX-034", "SELinux / AppArmor",                       "L4", "★★★"),
    ("LNX-050", "LNX-035", "Linux Security Hardening",                 "L4", "★★★"),
    ("LNX-051", "LNX-036", "Signals (SIGTERM, SIGKILL, SIGHUP)",       "L4", "★★★"),
    ("LNX-052", "LNX-037", "Zombie Processes",                         "L4", "★★★"),
    ("LNX-053", "LNX-040", "Linux Performance Tuning",                 "L4", "★★★"),
    ("LNX-054", None,       "eBPF (Extended Berkeley Packet Filter)",  "L4", "★★★"),
    ("LNX-055", None,       "perf / flamegraph",                       "L4", "★★★"),
    ("LNX-056", None,       "Heartbleed Impact on Linux Systems (2014)","L4","★★★"),
    ("LNX-057", None,       "Dirty COW Vulnerability (2016)",          "L4", "★★★"),
    ("LNX-058", None,       "NUMA Topology and CPU Affinity",          "L4", "★★★"),

    # L4.5 — ARCHITECT
    ("LNX-059", None,       "Linux Fleet Standardisation Strategy",    "L45","🔥"),
    ("LNX-060", None,       "Golden Image vs Immutable Infrastructure","L45","🔥"),
    ("LNX-061", None,       "Kernel Version Policy at Scale",          "L45","🔥"),
    ("LNX-062", None,       "Linux-Based Platform Engineering",        "L45","🔥"),

    # L5 — CREATOR
    ("LNX-063", None,       "Linux Kernel Architecture Deep Dive",     "L5", "🔬"),
    ("LNX-064", None,       "Kernel Development and Patch Contribution","L5","🔬"),
    ("LNX-065", None,       "Scheduler Algorithm Design (CFS, FIFO)",  "L5", "🔬"),
    ("LNX-066", None,       "VFS (Virtual File System) Architecture",  "L5", "🔬"),

    # META
    ("LNX-067", None,       "Unix Philosophy as Engineering Principle","META","🧠"),
    ("LNX-068", None,       "Everything-Is-a-File Thinking",           "META","🧠"),
    ("LNX-069", None,       "Observability-First System Navigation",   "META","🧠"),
]

OSY_KEYWORDS = [
    # L0 — ORIENTATION (new)
    ("OSY-001", None, "What Is an Operating System",                   "L0", "🌱"),
    ("OSY-002", None, "Why Operating Systems Exist",                   "L0", "🌱"),
    ("OSY-003", None, "The OS Abstraction Stack",                      "L0", "🌱"),
    ("OSY-004", None, "Major OS Families (Unix, Windows, RTOS)",       "L0", "🌱"),
    ("OSY-005", None, "How Hardware Becomes Software — A Map",         "L0", "🌱"),

    # L1 — FOUNDATIONAL
    ("OSY-006", "OSY-001", "Process",                                  "L1", "★☆☆"),
    ("OSY-007", "OSY-002", "Thread",                                   "L1", "★☆☆"),
    ("OSY-008", "OSY-004", "Process vs Thread",                        "L1", "★☆☆"),
    ("OSY-009", "OSY-007", "User Space vs Kernel Space",               "L1", "★☆☆"),
    ("OSY-010", "OSY-008", "System Call (syscall)",                    "L1", "★☆☆"),
    ("OSY-011", "OSY-009", "Virtual Memory",                           "L1", "★☆☆"),
    ("OSY-012", "OSY-018", "File Descriptor",                          "L1", "★☆☆"),
    ("OSY-013", "OSY-014", "Blocking IO",                              "L1", "★☆☆"),
    ("OSY-014", "OSY-015", "Non-Blocking IO",                          "L1", "★☆☆"),
    ("OSY-015", "OSY-024", "Mutex",                                    "L1", "★☆☆"),
    ("OSY-016", "OSY-028", "Deadlock",                                 "L1", "★☆☆"),
    ("OSY-017", None,       "CPU Scheduling Basics",                   "L1", "★☆☆"),
    ("OSY-018", None,       "Memory Allocation Basics",                "L1", "★☆☆"),

    # L2 — WORKING
    ("OSY-019", "OSY-003", "Fiber / Coroutine",                        "L2", "★★☆"),
    ("OSY-020", "OSY-005", "Context Switch",                           "L2", "★★☆"),
    ("OSY-021", "OSY-006", "Scheduler / Preemption",                   "L2", "★★☆"),
    ("OSY-022", "OSY-010", "Paging",                                   "L2", "★★☆"),
    ("OSY-023", "OSY-016", "Async IO",                                 "L2", "★★☆"),
    ("OSY-024", "OSY-025", "Semaphore",                                "L2", "★★☆"),
    ("OSY-025", "OSY-027", "Condition Variable",                       "L2", "★★☆"),
    ("OSY-026", "OSY-029", "Livelock",                                 "L2", "★★☆"),
    ("OSY-027", "OSY-030", "Starvation",                               "L2", "★★☆"),
    ("OSY-028", "OSY-031", "Fork / Exec",                              "L2", "★★☆"),
    ("OSY-029", "OSY-033", "Inode / File System",                      "L2", "★★☆"),
    ("OSY-030", None,       "Thread Pool Pattern",                     "L2", "★★☆"),
    ("OSY-031", None,       "Concurrency Anti-Patterns (Race Condition)","L2","★★☆"),

    # L3 — INTERMEDIATE
    ("OSY-032", "OSY-011", "Page Fault",                               "L3", "★★☆"),
    ("OSY-033", "OSY-012", "TLB (Translation Lookaside Buffer)",       "L3", "★★☆"),
    ("OSY-034", "OSY-013", "Memory-Mapped File (mmap)",                "L3", "★★☆"),
    ("OSY-035", "OSY-017", "epoll / kqueue / io_uring",                "L3", "★★☆"),
    ("OSY-036", "OSY-019", "Page Cache",                               "L3", "★★☆"),
    ("OSY-037", "OSY-026", "Spinlock",                                 "L3", "★★☆"),
    ("OSY-038", "OSY-032", "Signal Handling",                          "L3", "★★☆"),
    ("OSY-039", "OSY-034", "Swap / Thrashing",                         "L3", "★★☆"),
    ("OSY-040", None,       "Memory Profiling Tools (valgrind, heaptrack)","L3","★★☆"),
    ("OSY-041", None,       "I/O Scheduling Algorithms",               "L3", "★★☆"),
    ("OSY-042", None,       "OS Security — Privilege Escalation",      "L3", "★★☆"),
    ("OSY-043", None,       "Testing Concurrent Code",                 "L3", "★★☆"),

    # L4 — EXPERT
    ("OSY-044", "OSY-020", "Zero-Copy (sendfile)",                     "L4", "★★★"),
    ("OSY-045", "OSY-021", "NUMA",                                     "L4", "★★★"),
    ("OSY-046", "OSY-022", "Cache Line",                               "L4", "★★★"),
    ("OSY-047", "OSY-023", "False Sharing",                            "L4", "★★★"),
    ("OSY-048", "OSY-035", "Buddy System / Slab Allocator",            "L4", "★★★"),
    ("OSY-049", None,       "io_uring Deep Dive",                      "L4", "★★★"),
    ("OSY-050", None,       "Spectre and Meltdown (2018)",             "L4", "★★★"),
    ("OSY-051", None,       "Linux OOM Killer Behaviour",              "L4", "★★★"),
    ("OSY-052", None,       "Lock-Free Data Structures",               "L4", "★★★"),
    ("OSY-053", None,       "Memory Barriers and CPU Ordering",        "L4", "★★★"),

    # L4.5 — ARCHITECT
    ("OSY-054", None,       "OS Selection Framework (Linux, RTOS, BSD)","L45","🔥"),
    ("OSY-055", None,       "Kernel Tuning Strategy at Fleet Scale",   "L45","🔥"),
    ("OSY-056", None,       "Concurrency Architecture Patterns",       "L45","🔥"),
    ("OSY-057", None,       "Platform Thread Model Design",            "L45","🔥"),

    # L5 — CREATOR
    ("OSY-058", None,       "OS Kernel Architecture and Design",       "L5", "🔬"),
    ("OSY-059", None,       "Scheduling Algorithm Theory (CFS, EDF)",  "L5", "🔬"),
    ("OSY-060", None,       "Memory Manager Design (SLUB, SLOB)",      "L5", "🔬"),
    ("OSY-061", None,       "Formal Verification of OS Components",    "L5", "🔬"),

    # META
    ("OSY-062", None,       "Hardware-Software Co-design Thinking",    "META","🧠"),
    ("OSY-063", None,       "Performance Intuition from First Principles","META","🧠"),
    ("OSY-064", None,       "Latency Sources Mental Model",            "META","🧠"),
]

# ─────────────────────────────────────────────────────────────────────────────
# FRONTMATTER TEMPLATE FOR NEW FILES
# ─────────────────────────────────────────────────────────────────────────────

DIFF_MAP = {
    "L0":   "★☆☆",
    "L1":   "★☆☆",
    "L2":   "★★☆",
    "L3":   "★★☆",
    "L4":   "★★★",
    "L45":  "★★★",
    "L5":   "★★★",
    "META": "★★★",
}

CATEGORY_META = {
    "CSF": {
        "category": "CS Fundamentals — Paradigms",
        "tier": "tier-1-foundations",
        "folder": "CSF-cs-fundamentals",
        "parent": "CS Fundamentals — Paradigms",
        "dir": BASE / "CSF-cs-fundamentals",
    },
    "DSA": {
        "category": "Data Structures & Algorithms",
        "tier": "tier-1-foundations",
        "folder": "DSA-data-structures",
        "parent": "Data Structures & Algorithms",
        "dir": BASE / "DSA-data-structures",
    },
    "LNX": {
        "category": "Linux",
        "tier": "tier-1-foundations",
        "folder": "LNX-linux",
        "parent": "Linux",
        "dir": BASE / "LNX-linux",
    },
    "OSY": {
        "category": "Operating Systems",
        "tier": "tier-1-foundations",
        "folder": "OSY-operating-systems",
        "parent": "Operating Systems",
        "dir": BASE / "OSY-operating-systems",
    },
}

LEVEL_TAG_MAP = {
    "L0":   ["foundational", "mental-model"],
    "L1":   ["foundational", "first-principles"],
    "L2":   ["intermediate", "pattern"],
    "L3":   ["intermediate", "deep-dive", "tradeoff"],
    "L4":   ["advanced", "production", "deep-dive"],
    "L45":  ["advanced", "architecture", "bestpractice"],
    "L5":   ["advanced", "deep-dive", "first-principles"],
    "META": ["advanced", "mental-model", "bestpractice"],
}

def make_nav_order(new_id):
    return int(new_id.split("-")[1])

def make_permalink(code, title):
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    code_path = code.lower()
    return f"/{code_path}/{slug}/"

def sanitize_filename(new_id, title):
    safe = re.sub(r'[<>:"/\\|?*]', '', title)
    safe = safe.replace("/", "-")
    return f"{new_id} — {safe}.md"

def build_frontmatter(new_id, title, level, code, meta):
    diff = DIFF_MAP[level]
    tags = LEVEL_TAG_MAP[level]
    category_tag = code.lower()
    all_tags = [category_tag] + tags
    tags_yaml = "\n".join(f"  - {t}" for t in all_tags)
    nav = make_nav_order(new_id)
    permalink = make_permalink(code, title)
    return f"""---
id: {new_id}
title: {title}
category: {meta['category']}
tier: {meta['tier']}
folder: {meta['folder']}
difficulty: {diff}
depends_on:
used_by:
related:
tags:
{tags_yaml}
status: draft
version: 1
layout: default
parent: "{meta['parent']}"
nav_order: {nav}
permalink: {permalink}
---

# {new_id} — {title}

> Entry stub. Generate full content using Master Prompt v3.0.
"""

def process_category(code, keywords):
    meta = CATEGORY_META[code]
    d = meta["dir"]
    print(f"\n{'='*60}")
    print(f"Processing {code} ({len(keywords)} keywords)")
    print(f"{'='*60}")

    # Build old_id → old filename map
    old_files = {}
    for f in d.glob(f"{code}-*.md"):
        if f.name == "index.md":
            continue
        m = re.match(rf"({code}-\d+)", f.stem)
        if m:
            old_files[m.group(1)] = f

    # Step 1: Rename existing files to tmp names to avoid collisions
    tmp_renames = {}
    for new_id, old_id, title, level, diff in keywords:
        if old_id and old_id in old_files:
            src = old_files[old_id]
            tmp = src.parent / f"_tmp_{new_id}_{src.name}"
            src.rename(tmp)
            tmp_renames[new_id] = (tmp, old_id, title, level)
            print(f"  TMP: {src.name} → {tmp.name}")

    # Step 2: Rename tmp files to final names and update frontmatter
    for new_id, old_id, title, level, diff in keywords:
        if new_id in tmp_renames:
            tmp, old_id_, title_, level_ = tmp_renames[new_id]
            new_filename = sanitize_filename(new_id, title)
            dst = d / new_filename
            tmp.rename(dst)
            print(f"  RENAME: {old_id_} → {new_id} — {title}")
            # Update frontmatter
            content = dst.read_text(encoding="utf-8", errors="replace")
            # Replace id field
            content = re.sub(r'^id:\s*.+$', f'id: {new_id}', content, flags=re.MULTILINE)
            # Replace number field (older format)
            content = re.sub(r'^number:\s*.+$', f'id: {new_id}', content, flags=re.MULTILINE)
            # Update title
            content = re.sub(r'^title:\s*".+"$', f'title: "{title}"', content, flags=re.MULTILINE)
            content = re.sub(r"^title:\s*'.+'$", f'title: "{title}"', content, flags=re.MULTILINE)
            # Replace nav_order
            nav = make_nav_order(new_id)
            content = re.sub(r'^nav_order:\s*\d+$', f'nav_order: {nav}', content, flags=re.MULTILINE)
            # Update h1 heading
            content = re.sub(
                rf'^# {re.escape(old_id_)}.*$',
                f'# {new_id} — {title}',
                content, flags=re.MULTILINE
            )
            dst.write_text(content, encoding="utf-8")

    # Step 3: Create new (gap) files
    for new_id, old_id, title, level, diff in keywords:
        if not old_id:
            new_filename = sanitize_filename(new_id, title)
            dst = d / new_filename
            if dst.exists():
                print(f"  SKIP (exists): {new_filename}")
                continue
            fm = build_frontmatter(new_id, title, level, code, meta)
            dst.write_text(fm, encoding="utf-8")
            print(f"  CREATE: {new_filename}")

    # Step 4: Report any old files not in new list
    new_ids = {kw[0] for kw in keywords}
    old_ids_used = {kw[1] for kw in keywords if kw[1]}
    for old_id, f in old_files.items():
        if old_id not in old_ids_used:
            print(f"  WARNING: Old file NOT in new list: {f.name}")

if __name__ == "__main__":
    process_category("CSF", CSF_KEYWORDS)
    process_category("DSA", DSA_KEYWORDS)
    process_category("LNX", LNX_KEYWORDS)
    process_category("OSY", OSY_KEYWORDS)
    print("\nDone.")
