# 🎯 Category Keyword Generator — Master Prompt

---

```
═══════════════════════════════════════════════════════════════════════════
CATEGORY KEYWORD GENERATOR — MASTER PROMPT v1.0
═══════════════════════════════════════════════════════════════════════════

PURPOSE:
  Generate a complete, exhaustive keyword list for a given category
  covering ALL levels of knowledge from absolute beginner to
  creator/designer level — the person who designs the technology itself.

  The output is a structured keyword list ready to be used as input
  for dictionary entry generation (Master Prompt v2.0 + v3.0).

═══════════════════════════════════════════════════════════════════════════
SECTION 1: KNOWLEDGE LEVEL FRAMEWORK
═══════════════════════════════════════════════════════════════════════════

Every category must be covered across FIVE levels.
Each level has a precise definition and a test question.

─────────────────────────────────────────────────────────────────────────
LEVEL 1 — FOUNDATIONAL  ★☆☆
─────────────────────────────────────────────────────────────────────────

  WHO:
    Someone who has never used this technology.
    A student, a career switcher, a developer
    from a completely different domain.

  WHAT THEY NEED:
    What is this? Why does it exist?
    What problem does it solve?
    What does it look like to use it?
    What are the core building blocks?
    What vocabulary do I need to read a tutorial?

  TEST QUESTION:
    "Can a complete beginner read this keyword
     list and understand what they need to learn
     before touching the technology?"

  CHARACTERISTICS OF FOUNDATIONAL KEYWORDS:
    - Definitions of core concepts
    - The "what" — not the "how"
    - Building blocks the rest depends on
    - Vocabulary the ecosystem uses universally
    - Concepts that appear in every tutorial

  EXAMPLES:
    Java:   JVM, Class, Object, Variable, Method
    React:  Component, JSX, Props, State
    Docker: Container, Image, Dockerfile
    SQL:    Table, Row, Column, SELECT, WHERE

─────────────────────────────────────────────────────────────────────────
LEVEL 2 — WORKING  ★★☆  (lower half)
─────────────────────────────────────────────────────────────────────────

  WHO:
    A developer who can use the technology
    for common tasks without constant help.
    Junior to mid-level practitioner.

  WHAT THEY NEED:
    How do I use this correctly?
    What are the common patterns?
    What mistakes do beginners make?
    How do I connect this to other tools?
    What does production usage look like?

  TEST QUESTION:
    "Can someone at this level build and ship
     a basic production feature without
     breaking anything obvious?"

  CHARACTERISTICS:
    - Common patterns and idioms
    - Standard library / framework features
    - Basic configuration and setup
    - Typical error types and fixes
    - Integration with other common tools

  EXAMPLES:
    Java:   Collections, Generics, Exception handling
    React:  useEffect, useState, Event handlers
    Docker: docker-compose, volumes, networking
    SQL:    JOINs, Indexes, Transactions

─────────────────────────────────────────────────────────────────────────
LEVEL 3 — INTERMEDIATE  ★★☆  (upper half)
─────────────────────────────────────────────────────────────────────────

  WHO:
    A developer who builds features independently,
    reviews others' code, and makes design decisions.
    Mid to senior level practitioner.

  WHAT THEY NEED:
    Why does this work the way it does?
    How do I choose between alternatives?
    How do I debug non-obvious issues?
    How do I optimise for performance?
    What are the trade-offs of each approach?

  TEST QUESTION:
    "Can someone at this level make correct
     design decisions and explain their
     reasoning to a team?"

  CHARACTERISTICS:
    - Internals and mechanisms
    - Performance tuning basics
    - Architectural patterns
    - Trade-off analysis
    - Non-obvious failure modes
    - Security considerations

  EXAMPLES:
    Java:   GC tuning, Thread pools, JVM flags
    React:  Reconciliation, Fiber, useMemo
    Docker: Layer caching, Multi-stage builds
    SQL:    Query execution plan, Index types

─────────────────────────────────────────────────────────────────────────
LEVEL 4 — EXPERT  ★★★
─────────────────────────────────────────────────────────────────────────

  WHO:
    A senior or staff engineer who owns systems
    in production, mentors others, and solves
    the hardest problems in the domain.

  WHAT THEY NEED:
    What happens at extreme scale or load?
    How does the runtime/engine actually work?
    What are the edge cases that break things?
    How do I diagnose issues in production?
    What are the known bugs and limitations?
    How does this interact with other systems
    in unexpected ways?

  TEST QUESTION:
    "Can someone at this level diagnose a
     production incident at 3am using only
     their knowledge of this technology?"

  CHARACTERISTICS:
    - Deep internals (JVM, V8, kernel)
    - Production diagnostic patterns
    - At-scale failure modes
    - Advanced configuration and tuning
    - Security vulnerabilities and mitigations
    - Interaction with OS / network / hardware
    - Historical context and design decisions

  EXAMPLES:
    Java:   GC algorithm internals, Safepoints,
            JIT compilation pipeline, TLAB
    React:  Scheduler internals, Lane priority,
            Concurrent rendering algorithm
    Docker: Namespace / cgroup internals,
            overlay filesystem, seccomp
    SQL:    MVCC internals, WAL, Buffer pool

─────────────────────────────────────────────────────────────────────────
LEVEL 5 — CREATOR / DESIGNER  🔬
─────────────────────────────────────────────────────────────────────────

  WHO:
    The person who DESIGNS the technology,
    writes the specification, builds the
    runtime, or creates the framework.
    Also: the engineer who extends the
    technology in fundamental ways.

  WHAT THEY NEED:
    What fundamental computer science
    problems does this solve?
    What were the alternatives considered
    when this was designed?
    What are the theoretical limits?
    How does this technology compose with
    other technologies at the deepest level?
    What would a better version look like?
    What research papers underpin this?

  TEST QUESTION:
    "Could someone at this level write a
     replacement for this technology, or
     meaningfully contribute to its specification?"

  CHARACTERISTICS:
    - Foundational CS theory behind the technology
    - Specification-level knowledge
    - Alternative design explorations
    - Research / academic foundations
    - Cross-technology interaction at system level
    - Historical evolution and design rationale
    - Known open problems in the field

  EXAMPLES:
    Java:   JVM specification, Bytecode design,
            GC algorithm research (G1, ZGC theory),
            Project Loom / Valhalla design rationale
    React:  Algebraic effects, Concurrent rendering
            research, Scheduling theory
    Docker: Container security model theory,
            OCI specification design
    SQL:    Relational algebra, MVCC theory,
            Isolation level formalism (Adya 1999)

═══════════════════════════════════════════════════════════════════════════
SECTION 2: KEYWORD GENERATION RULES
═══════════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────────
RULE 1: COVERAGE MUST BE COMPLETE
─────────────────────────────────────────────────────────────────────────

  For EVERY level, ask:
    "Is there any concept at this level that
     a practitioner would encounter that is
     NOT in this list?"

  If yes: add it.
  Do not self-censor for length.
  A complete list is better than a short list.

─────────────────────────────────────────────────────────────────────────
RULE 2: KEYWORDS MUST BE ATOMIC
─────────────────────────────────────────────────────────────────────────

  Each keyword = one concept.
  Not "authentication and authorisation" — split it.
  Not "GET, POST, PUT methods" — one per line.
  Not "Spring Boot configuration and tuning" — split it.

  Exception: tightly coupled pairs that are always
  taught and understood together:
    "Encoding vs Encryption vs Hashing"
    "var vs let vs const"
    "Stack vs Heap"
  These may stay together as one keyword.

─────────────────────────────────────────────────────────────────────────
RULE 3: DIFFICULTY IS ASSIGNED PER LEVEL
─────────────────────────────────────────────────────────────────────────

  Level 1 Foundational:    always ★☆☆
  Level 2 Working:         always ★★☆ (lower)
  Level 3 Intermediate:    always ★★☆ (upper)
  Level 4 Expert:          always ★★★
  Level 5 Creator:         always ★★★ (marked 🔬)

  In the output table:
    ★☆☆ = Foundational
    ★★☆ = Intermediate
    ★★★ = Deep-dive
    🔬  = Creator/Designer level

─────────────────────────────────────────────────────────────────────────
RULE 4: KEYWORDS BUILD ON EACH OTHER
─────────────────────────────────────────────────────────────────────────

  Each level assumes complete knowledge of
  all levels below it.

  Level 2 keywords should only reference
  Level 1 concepts as prerequisites.

  Level 5 keywords may reference concepts
  from any level — including other categories.

  The list must be learnable in order:
  Level 1 → 2 → 3 → 4 → 5.
  No Level 3 keyword should require knowledge
  from Level 4 to understand.

─────────────────────────────────────────────────────────────────────────
RULE 5: INCLUDE ALL THREE KNOWLEDGE TYPES
─────────────────────────────────────────────────────────────────────────

  For each level, ensure coverage of:

  CONCEPTUAL knowledge:
    What things are and why they exist.
    Example: "What is a GC Root?"

  PROCEDURAL knowledge:
    How to do things — steps, patterns, tools.
    Example: "How to read GC logs"

  SITUATIONAL knowledge:
    When to use what, and why not to use it.
    Example: "When to use ZGC vs G1GC"

─────────────────────────────────────────────────────────────────────────
RULE 6: PRODUCTION KEYWORDS ARE MANDATORY AT L3+
─────────────────────────────────────────────────────────────────────────

  Every Level 3, 4, and 5 section MUST include:
    - At least 2 diagnostic / observability keywords
      (tools, commands, metrics, logs)
    - At least 2 failure mode keywords
      (what breaks, what to watch for)
    - At least 1 tuning / optimisation keyword

─────────────────────────────────────────────────────────────────────────
RULE 7: SECURITY KEYWORDS ARE MANDATORY AT L3+
─────────────────────────────────────────────────────────────────────────

  Every Level 3, 4, and 5 section MUST include:
    At least 1 security-relevant keyword for
    this specific technology domain.

─────────────────────────────────────────────────────────────────────────
RULE 8: NO DUPLICATES ACROSS LEVELS
─────────────────────────────────────────────────────────────────────────

  Each keyword appears EXACTLY ONCE.
  If a concept is both foundational and deep:
    Place it at its FIRST introduction level.
    Later levels can build on it without
    re-listing it.

─────────────────────────────────────────────────────────────────────────
RULE 9: IDs ARE ASSIGNED SEQUENTIALLY WITHIN CATEGORY
─────────────────────────────────────────────────────────────────────────

  Use the category code from Master Prompt v3.0.
  Start at [CODE]-001 if new category.
  Continue from last ID if extending existing.
  IDs are assigned in order within each level
  (all L1 keywords first, then L2, etc.)

═══════════════════════════════════════════════════════════════════════════
SECTION 3: OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────────
3.1 HEADER BLOCK
─────────────────────────────────────────────────────────────────────────

  Output begins with:

  ═══════════════════════════════════════════════════
  CATEGORY: [Full Category Name]
  CODE:      [3-letter code]
  TIER:      [tier-N-name]
  FOLDER:    [CODE-folder-name]
  TOTAL:     [N] keywords across 5 levels
  ═══════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────────
3.2 LEVEL BLOCK FORMAT
─────────────────────────────────────────────────────────────────────────

  Each level section uses this exact structure:

  ───────────────────────────────────────────────────
  LEVEL [N] — [LEVEL NAME]  [STAR RATING]
  [N] keywords
  ───────────────────────────────────────────────────

  | ID        | Keyword                        | Difficulty |
  |-----------|--------------------------------|------------|
  | [CODE]-001| [Keyword Name]                 | ★☆☆        |
  | [CODE]-002| [Keyword Name]                 | ★☆☆        |
  ...

─────────────────────────────────────────────────────────────────────────
3.3 SUMMARY TABLE
─────────────────────────────────────────────────────────────────────────

  After all 5 levels, output:

  ═══════════════════════════════════════════════════
  SUMMARY
  ═══════════════════════════════════════════════════

  | Level | Name              | Count | ID Range          |
  |-------|-------------------|-------|-------------------|
  | L1    | Foundational      | N     | [CODE]-001–0NN    |
  | L2    | Working           | N     | [CODE]-0NN–0NN    |
  | L3    | Intermediate      | N     | [CODE]-0NN–0NN    |
  | L4    | Expert            | N     | [CODE]-0NN–0NN    |
  | L5    | Creator/Designer  | N     | [CODE]-0NN–0NN    |
  | TOTAL |                   | N     | [CODE]-001–0NN    |

─────────────────────────────────────────────────────────────────────────
3.4 LEARNING PATH NOTE
─────────────────────────────────────────────────────────────────────────

  After the summary, output:

  ═══════════════════════════════════════════════════
  LEARNING PATH
  ═══════════════════════════════════════════════════

  PREREQUISITE CATEGORIES:
  [List categories that should be studied BEFORE
   this one, with their codes]
  Example: Understand CSF (CS Fundamentals) and
           DSA (Data Structures) before JVM internals.

  PARALLEL CATEGORIES:
  [List categories best studied alongside this one]
  Example: Study JCC (Java Concurrency) alongside JVM.

  NEXT CATEGORIES:
  [List categories to study AFTER this one]
  Example: After JVM internals, study SPR (Spring Core).

  ENTRY POINT FOR NEW LEARNERS:
  Start at [CODE]-001 — [First Keyword Name]

  JUMP IN FOR PRACTITIONERS:
  Start at [CODE]-[NNN] — [First L3 Keyword Name]

─────────────────────────────────────────────────────────────────────────
3.5 CROSS-CATEGORY DEPENDENCIES
─────────────────────────────────────────────────────────────────────────

  After learning path, output:

  ═══════════════════════════════════════════════════
  CROSS-CATEGORY DEPENDENCIES
  ═══════════════════════════════════════════════════

  Keywords in this category that depend on
  concepts from OTHER categories:

  | This Keyword  | Depends On         | Category |
  |---------------|--------------------|----------|
  | JVM-036       | DSA-048 (B-Tree)   | DSA      |
  | JVM-028       | OSY-012 (Threading)| OSY      |

═══════════════════════════════════════════════════════════════════════════
SECTION 4: QUALITY CHECKS
═══════════════════════════════════════════════════════════════════════════

Before finalising output, verify:

COMPLETENESS CHECK:
  ☐ L1: Does list cover all concepts a beginner
        needs to start learning this technology?
  ☐ L2: Does list cover what a developer needs
        to use this in a real project?
  ☐ L3: Does list cover what an engineer needs
        to make design decisions?
  ☐ L4: Does list cover what an expert needs
        to diagnose production incidents?
  ☐ L5: Does list cover what a creator needs
        to redesign or extend the technology?

BALANCE CHECK:
  ☐ No level is significantly shorter than others
    (each level should have 10-30+ keywords
     for a rich technology domain)
  ☐ Conceptual / Procedural / Situational
    knowledge all represented at each level

PRODUCTION COVERAGE (L3, L4, L5):
  ☐ At least 2 diagnostic keywords per level
  ☐ At least 2 failure mode keywords per level
  ☐ At least 1 tuning keyword per level
  ☐ At least 1 security keyword per level

ATOMICITY CHECK:
  ☐ Each keyword is a single concept
  ☐ No keyword is a category (too broad)
  ☐ No keyword is a trivial sub-concept
    of another keyword on the same level

ID CHECK:
  ☐ IDs are sequential, no gaps
  ☐ Code matches category from registry
  ☐ Starts at correct number
    (001 if new, continues if extending)

LEARNING ORDER CHECK:
  ☐ L1 keywords do not require L2+ knowledge
  ☐ L2 keywords do not require L3+ knowledge
  ☐ Each level is learnable without skipping ahead

═══════════════════════════════════════════════════════════════════════════
SECTION 5: INVOCATION — HOW TO USE THIS PROMPT
═══════════════════════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────────────────────
NEW CATEGORY — GENERATE ALL LEVELS:
─────────────────────────────────────────────────────────────────────────

  Generate complete keyword list for category:

    Category:  Java & JVM Internals
    Code:      JVM
    Tier:      tier-3-java
    Folder:    JVM-java-jvm-internals
    Starting ID: JVM-001

  Cover ALL five levels:
    L1 — Foundational    (★☆☆)
    L2 — Working         (★★☆)
    L3 — Intermediate    (★★☆)
    L4 — Expert          (★★★)
    L5 — Creator         (🔬)

  Follow Category Keyword Generator prompt exactly.
  Apply all rules from Section 2.
  Use output format from Section 3.
  Run quality checks from Section 4.

─────────────────────────────────────────────────────────────────────────
EXISTING CATEGORY — ADD MISSING LEVELS:
─────────────────────────────────────────────────────────────────────────

  Extend keyword list for category:

    Category:      Java & JVM Internals
    Code:          JVM
    Last ID used:  JVM-050
    Next ID:       JVM-051

  Already covered:  L1, L2, L3
  Generate ONLY:    L4 (Expert) and L5 (Creator)

  Continue sequential IDs from JVM-051.
  Follow Category Keyword Generator prompt exactly.

─────────────────────────────────────────────────────────────────────────
SINGLE LEVEL GENERATION:
─────────────────────────────────────────────────────────────────────────

  Generate Level 4 (Expert) keywords only for:

    Category:    Security
    Code:        SEC
    Last ID:     SEC-050
    Next ID:     SEC-051

  Generate ONLY L4 keywords.
  Continue sequential IDs from SEC-051.
  Follow Category Keyword Generator prompt exactly.

─────────────────────────────────────────────────────────────────────────
GAP ANALYSIS — FIND MISSING KEYWORDS:
─────────────────────────────────────────────────────────────────────────

  Analyse existing keyword list for category:

    Category: Security (SEC)

  [paste existing keyword list here]

  Identify:
    1. Which levels are well covered?
    2. Which levels have gaps?
    3. What specific keywords are missing
       at each level?
    4. What cross-category dependencies
       are missing?

  Output: gap analysis + list of missing keywords
  with suggested IDs.

─────────────────────────────────────────────────────────────────────────
CROSS-TECHNOLOGY CATEGORY:
─────────────────────────────────────────────────────────────────────────

  Generate complete keyword list for category:

    Category:    System Design
    Code:        SYD
    Tier:        tier-5-distributed-architecture
    Note:        This category spans multiple
                 technology domains. Include
                 keywords for each domain
                 (databases, networking, caching,
                 compute, storage) at each level.

  Cover ALL five levels.
  Include domain-specific sub-sections
  within each level where appropriate.
  Follow Category Keyword Generator prompt exactly.

═══════════════════════════════════════════════════════════════════════════
SECTION 6: LEVEL DISTRIBUTION GUIDELINES
═══════════════════════════════════════════════════════════════════════════

For a TYPICAL rich technology category,
expect this distribution:

  L1 Foundational:    15–25 keywords
    (core vocabulary, building blocks)

  L2 Working:         20–35 keywords
    (usage patterns, common features)

  L3 Intermediate:    25–40 keywords
    (internals, design choices, trade-offs)

  L4 Expert:          25–40 keywords
    (production, scale, failure modes)

  L5 Creator:         10–20 keywords
    (theory, specification, research)

  TOTAL:              95–160 keywords
    for a rich domain

For NARROW or FOCUSED categories:
  (e.g. npm, Git, Document Generation)
  Each level may have 5–15 keywords.
  Total: 30–60 keywords.

For BROAD cross-domain categories:
  (e.g. System Design, Distributed Systems)
  Each level may have 30–60 keywords.
  Total: 150–250 keywords.

─────────────────────────────────────────────────────────────────────────
LEVEL DISTRIBUTION BY CATEGORY TYPE:
─────────────────────────────────────────────────────────────────────────

  RUNTIME / ENGINE (JVM, V8, Node.js):
    L4 and L5 are largest
    (deep internals dominate)

  FRAMEWORK (Spring, React, Angular):
    L2 and L3 are largest
    (usage patterns dominate)

  PROTOCOL / STANDARD (HTTP, TCP, SQL):
    L1 and L5 are largest
    (fundamentals + specification dominate)

  INFRASTRUCTURE (Docker, K8s, Terraform):
    L2 and L4 are largest
    (setup patterns + production ops dominate)

  DOMAIN (Financial Services, AI Agents):
    L3 and L4 are largest
    (design decisions + production dominate)

═══════════════════════════════════════════════════════════════════════════
SECTION 7: EXAMPLE OUTPUT
═══════════════════════════════════════════════════════════════════════════

Input:
  Category: Security
  Code:     SEC
  Tier:     tier-2-networking-security
  Folder:   SEC-security
  Start ID: SEC-001

─────────────────────────────────────────────────────────────────────────
EXAMPLE OUTPUT (abbreviated):
─────────────────────────────────────────────────────────────────────────

  ═══════════════════════════════════════════════════
  CATEGORY: Security
  CODE:      SEC
  TIER:      tier-2-networking-security
  FOLDER:    SEC-security
  TOTAL:     112 keywords across 5 levels
  ═══════════════════════════════════════════════════

  ───────────────────────────────────────────────────
  LEVEL 1 — FOUNDATIONAL  ★☆☆
  18 keywords
  ───────────────────────────────────────────────────

  | ID      | Keyword                               | Difficulty |
  |---------|---------------------------------------|------------|
  | SEC-001 | CIA Triad                             | ★☆☆        |
  | SEC-002 | Authentication vs Authorisation       | ★☆☆        |
  | SEC-003 | Encoding (Base64)                     | ★☆☆        |
  | SEC-004 | Hashing Overview                      | ★☆☆        |
  | SEC-005 | Encryption Overview                   | ★☆☆        |
  | SEC-006 | HTTPS Overview                        | ★☆☆        |
  | SEC-007 | Password Security Basics              | ★☆☆        |
  | SEC-008 | Firewall (Conceptual)                 | ★☆☆        |
  | SEC-009 | Principle of Least Privilege          | ★☆☆        |
  | SEC-010 | Social Engineering                    | ★☆☆        |
  | SEC-011 | Phishing                              | ★☆☆        |
  | SEC-012 | Malware Overview                      | ★☆☆        |
  | SEC-013 | Security vs Privacy                   | ★☆☆        |
  | SEC-014 | Threat vs Vulnerability vs Risk       | ★☆☆        |
  | SEC-015 | Security Policy                       | ★☆☆        |
  | SEC-016 | Attack Surface (Basic)                | ★☆☆        |
  | SEC-017 | Zero Trust (Conceptual)               | ★☆☆        |
  | SEC-018 | Security by Design (Basic)            | ★☆☆        |

  ───────────────────────────────────────────────────
  LEVEL 2 — WORKING  ★★☆
  22 keywords
  ───────────────────────────────────────────────────

  | ID      | Keyword                               | Difficulty |
  |---------|---------------------------------------|------------|
  | SEC-019 | Session-Based Authentication          | ★★☆        |
  | SEC-020 | Token-Based Authentication            | ★★☆        |
  | SEC-021 | JWT Anatomy                           | ★★☆        |
  | SEC-022 | Hashing (Bcrypt, Argon2)              | ★★☆        |
  | SEC-023 | CSRF                                  | ★★☆        |
  | SEC-024 | XSS                                   | ★★☆        |
  | SEC-025 | SQL Injection                         | ★★☆        |
  | SEC-026 | Parameterized Queries                 | ★★☆        |
  | SEC-027 | Input Sanitization vs Escaping        | ★★☆        |
  | SEC-028 | HTTPS / TLS (Practical)               | ★★☆        |
  | SEC-029 | API Key Security                      | ★★☆        |
  | SEC-030 | .env File Pattern                     | ★★☆        |
  | SEC-031 | OWASP Top 10 Overview                 | ★★☆        |
  | SEC-032 | Brute-Force Attack                    | ★★☆        |
  | SEC-033 | Rate Limiting for Security            | ★★☆        |
  | SEC-034 | Role-Based Access Control (RBAC)      | ★★☆        |
  | SEC-035 | HttpOnly Cookie                       | ★★☆        |
  | SEC-036 | Secure Cookie Flag                    | ★★☆        |
  | SEC-037 | CORS Security Implications            | ★★☆        |
  | SEC-038 | Man-in-the-Middle Attack              | ★★☆        |
  | SEC-039 | Password Storage Best Practices       | ★★☆        |
  | SEC-040 | MFA / 2FA                             | ★★☆        |

  ───────────────────────────────────────────────────
  LEVEL 3 — INTERMEDIATE  ★★☆
  28 keywords
  ───────────────────────────────────────────────────

  | ID      | Keyword                               | Difficulty |
  |---------|---------------------------------------|------------|
  | SEC-041 | OAuth 2.0 Authorization Code Flow     | ★★☆        |
  | SEC-042 | OAuth 2.0 Client Credentials Flow     | ★★☆        |
  | SEC-043 | OpenID Connect (OIDC)                 | ★★☆        |
  | SEC-044 | JWT Security Vulnerabilities          | ★★☆        |
  | SEC-045 | Symmetric vs Asymmetric Encryption    | ★★☆        |
  | SEC-046 | Public Key / Private Key              | ★★☆        |
  | SEC-047 | TLS Certificate Lifecycle             | ★★☆        |
  | SEC-048 | Stored XSS vs Reflected XSS           | ★★☆        |
  | SEC-049 | DOM-Based XSS                         | ★★☆        |
  | SEC-050 | SSRF                                  | ★★☆        |
  | SEC-051 | Command Injection                     | ★★☆        |
  | SEC-052 | Insecure Deserialization              | ★★☆        |
  | SEC-053 | Threat Modeling (STRIDE)              | ★★☆        |
  | SEC-054 | Security Headers                      | ★★☆        |
  | SEC-055 | Content Security Policy (CSP)         | ★★☆        |
  | SEC-056 | SameSite Cookie                       | ★★☆        |
  | SEC-057 | ABAC (Attribute-Based Access Control) | ★★☆        |
  | SEC-058 | SAML Overview                         | ★★☆        |
  | SEC-059 | SSO (Single Sign-On)                  | ★★☆        |
  | SEC-060 | Secrets Management                    | ★★☆        |
  | SEC-061 | SAST (Static Analysis Security)       | ★★☆        |
  | SEC-062 | Dependency Scanning                   | ★★☆        |
  | SEC-063 | Credential Stuffing                   | ★★☆        |
  | SEC-064 | Account Lockout Policy                | ★★☆        |
  | SEC-065 | Replay Attack                         | ★★☆        |
  | SEC-066 | Timing Attack                         | ★★☆        |
  | SEC-067 | WAF (Web Application Firewall)        | ★★☆        |
  | SEC-068 | DDoS Protection Strategies            | ★★☆        |

  ───────────────────────────────────────────────────
  LEVEL 4 — EXPERT  ★★★
  30 keywords
  ───────────────────────────────────────────────────

  | ID      | Keyword                               | Difficulty |
  |---------|---------------------------------------|------------|
  | SEC-069 | PKI (Public Key Infrastructure)       | ★★★        |
  | SEC-070 | Certificate Authority Chain           | ★★★        |
  | SEC-071 | Certificate Pinning                   | ★★★        |
  | SEC-072 | Key Management                        | ★★★        |
  | SEC-073 | HSM (Hardware Security Module)        | ★★★        |
  | SEC-074 | Key Rotation Strategy                 | ★★★        |
  | SEC-075 | Envelope Encryption                   | ★★★        |
  | SEC-076 | JWT Algorithm Confusion Attack        | ★★★        |
  | SEC-077 | Indirect Prompt Injection             | ★★★        |
  | SEC-078 | OAuth 2.0 PKCE                        | ★★★        |
  | SEC-079 | Supply Chain Attack                   | ★★★        |
  | SEC-080 | SBOM (Software Bill of Materials)     | ★★★        |
  | SEC-081 | Zero Trust Architecture (Deep)        | ★★★        |
  | SEC-082 | mTLS (Mutual TLS)                     | ★★★        |
  | SEC-083 | DAST (Dynamic Analysis Security)      | ★★★        |
  | SEC-084 | Penetration Testing                   | ★★★        |
  | SEC-085 | Red Team / Blue Team                  | ★★★        |
  | SEC-086 | CVSS Score                            | ★★★        |
  | SEC-087 | SIEM (Security Information & Events)  | ★★★        |
  | SEC-088 | Security Logging and Monitoring       | ★★★        |
  | SEC-089 | Incident Response                     | ★★★        |
  | SEC-090 | RASP (Runtime Application Protection) | ★★★        |
  | SEC-091 | Side-Channel Attack                   | ★★★        |
  | SEC-092 | Memory Safety Vulnerabilities         | ★★★        |
  | SEC-093 | OWASP LLM Top 10                      | ★★★        |
  | SEC-094 | Agent Permission Model                | ★★★        |
  | SEC-095 | Defense in Depth (Architecture)       | ★★★        |
  | SEC-096 | Compliance-Driven Security (SOX, PCI) | ★★★        |
  | SEC-097 | Container Security Hardening          | ★★★        |
  | SEC-098 | Network Segmentation Security         | ★★★        |

  ───────────────────────────────────────────────────
  LEVEL 5 — CREATOR / DESIGNER  🔬
  14 keywords
  ───────────────────────────────────────────────────

  | ID      | Keyword                               | Difficulty |
  |---------|---------------------------------------|------------|
  | SEC-099 | Cryptographic Primitive Design        | 🔬         |
  | SEC-100 | Formal Security Proofs                | 🔬         |
  | SEC-101 | Provable Security (Reduction Theory)  | 🔬         |
  | SEC-102 | Elliptic Curve Cryptography (Theory)  | 🔬         |
  | SEC-103 | Post-Quantum Cryptography             | 🔬         |
  | SEC-104 | Secure Multiparty Computation         | 🔬         |
  | SEC-105 | Zero-Knowledge Proofs                 | 🔬         |
  | SEC-106 | Homomorphic Encryption                | 🔬         |
  | SEC-107 | TLS Protocol Design Rationale         | 🔬         |
  | SEC-108 | OAuth 2.0 Specification Design        | 🔬         |
  | SEC-109 | Capability-Based Security Model       | 🔬         |
  | SEC-110 | Security Protocol Verification (BAN)  | 🔬         |
  | SEC-111 | Threat Modeling Formal Methods        | 🔬         |
  | SEC-112 | Applied Cryptography Research         | 🔬         |

  ═══════════════════════════════════════════════════
  SUMMARY
  ═══════════════════════════════════════════════════

  | Level | Name              | Count | ID Range          |
  |-------|-------------------|-------|-------------------|
  | L1    | Foundational      | 18    | SEC-001 – SEC-018 |
  | L2    | Working           | 22    | SEC-019 – SEC-040 |
  | L3    | Intermediate      | 28    | SEC-041 – SEC-068 |
  | L4    | Expert            | 30    | SEC-069 – SEC-098 |
  | L5    | Creator/Designer  | 14    | SEC-099 – SEC-112 |
  | TOTAL |                   | 112   | SEC-001 – SEC-112 |

  ═══════════════════════════════════════════════════
  LEARNING PATH
  ═══════════════════════════════════════════════════

  PREREQUISITE CATEGORIES:
    NET (Networking) — understand TCP/IP, TLS basics
    API (HTTP & APIs) — understand HTTP, cookies, headers

  PARALLEL CATEGORIES:
    API (HTTP & APIs) — security and API design intertwined
    CSF (CS Fundamentals) — cryptography needs math basics

  NEXT CATEGORIES:
    MSV (Microservices) — apply security in distributed systems
    K8S (Kubernetes) — container and cluster security
    AWS (Cloud) — cloud IAM and secrets management

  ENTRY POINT FOR NEW LEARNERS:
    Start at SEC-001 — CIA Triad

  JUMP IN FOR PRACTITIONERS:
    Start at SEC-041 — OAuth 2.0 Authorization Code Flow

═══════════════════════════════════════════════════════════════════════════
END OF CATEGORY KEYWORD GENERATOR PROMPT v1.0
═══════════════════════════════════════════════════════════════════════════
```

---

## 💡 How to Invoke

**Generate a complete new category:**
```
Generate complete keyword list for category:

  Category:    Java & JVM Internals
  Code:        JVM
  Tier:        tier-3-java
  Folder:      JVM-java-jvm-internals
  Starting ID: JVM-001

Cover ALL five levels (L1 through L5).
Follow the Category Keyword Generator prompt exactly.
```

**Extend an existing category with missing levels:**
```
Extend keyword list for category:

  Category:    Kubernetes
  Code:        K8S
  Last ID:     K8S-060
  Next ID:     K8S-061
  Generate:    L4 (Expert) and L5 (Creator) only

Follow the Category Keyword Generator prompt exactly.
```

**Gap analysis on existing list:**
```
Analyse this keyword list for category Security (SEC)
and identify gaps at each level:

[paste existing keyword list]

Follow the Category Keyword Generator prompt exactly.
Output: gap analysis + missing keywords with IDs.
```