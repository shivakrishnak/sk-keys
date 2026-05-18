# 🚫 LEGACY FILE - Single-Category Keyword Generator - Prompt v2.0

> **STATUS: LEGACY / OUTDATED.** This file references an old folder structure
> (`docs/` paths), old numeric IDs (1-45 categories), and a 20-section entry
> format. It is retained for historical reference only.
>
> **For current keyword generation:** use `MASTERY_OS_PROMPT.md` v4.1
> (24 rules, 18 quality checks, CODE-NNN ID system).
>
> **For current entry generation:** use `ENTRY_GENERATOR_PROMPT.md` v4.0
> (24 sections, 19 teaching principles).

---

# Original: Single-Category Keyword Generator - Prompt v2.0

> **Usage:** Set the `TARGET_CATEGORY_ID` below, then paste this entire prompt into an AI assistant.
> The agent will generate every missing keyword entry for that category only, 10 files at a time.

---

```
═══════════════════════════════════════════════════════════════════════
CONFIGURATION - SET THIS BEFORE RUNNING
═══════════════════════════════════════════════════════════════════════

  TARGET_CATEGORY_ID: <SET ID HERE - e.g. 16>

  Look up the ID in the Final Complete Category Summary table below:

  | ID | Category                       | Range        | Count |
  |----|--------------------------------|--------------|-------|
  |  1 | CS Fundamentals - Paradigms    | 001–030      |    30 |
  |  2 | Data Structures & Algorithms   | 031–090      |    60 |
  |  3 | Operating Systems              | 091–125      |    35 |
  |  4 | Linux                          | 126–165      |    40 |
  |  5 | Networking                     | 166–205      |    40 |
  |  6 | HTTP & APIs                    | 206–260      |    55 |
  |  7 | Java & JVM Internals           | 261–310      |    50 |
  |  8 | Java Language                  | 311–330      |    20 |
  |  9 | Java Concurrency               | 331–370      |    40 |
  | 10 | Spring Core                    | 371–410      |    40 |
  | 11 | Database Fundamentals          | 411–450      |    40 |
  | 12 | NoSQL & Distributed Databases  | 451–475      |    25 |
  | 13 | Caching                        | 476–495      |    20 |
  | 14 | Data Fundamentals              | 496–530      |    35 |
  | 15 | Big Data & Streaming           | 531–570      |    40 |
  | 16 | Distributed Systems            | 571–625      |    55 |
  | 17 | Microservices                  | 626–680      |    55 |
  | 18 | System Design                  | 681–725      |    45 |
  | 19 | Software Architecture Patterns | 726–765      |    40 |
  | 20 | Design Patterns                | 766–820      |    55 |
  | 21 | Containers                     | 821–855      |    35 |
  | 22 | Kubernetes                     | 856–915      |    60 |
  | 23 | Cloud - AWS                    | 916–955      |    40 |
  | 24 | Cloud - Azure                  | 956–990      |    35 |
  | 25 | CI/CD                          | 991–1030     |    40 |
  | 26 | Git & Branching Strategy       | 1031–1065    |    35 |
  | 27 | Maven & Build Tools (Java)     | 1066–1095    |    30 |
  | 28 | Code Quality                   | 1096–1130    |    35 |
  | 29 | Testing                        | 1131–1175    |    45 |
  | 30 | Observability & SRE            | 1176–1210    |    35 |
  | 31 | HTML                           | 1211–1240    |    30 |
  | 32 | CSS                            | 1241–1290    |    50 |
  | 33 | JavaScript                     | 1291–1370    |    80 |
  | 34 | TypeScript                     | 1371–1420    |    50 |
  | 35 | React                          | 1421–1480    |    60 |
  | 36 | Node.js                        | 1481–1510    |    30 |
  | 37 | npm & Package Management       | 1511–1530    |    20 |
  | 38 | Webpack & Build Tools          | 1531–1580    |    50 |
  | 39 | AI Foundations                 | 1581–1620    |    40 |
  | 40 | LLMs & Prompt Engineering      | 1621–1660    |    40 |
  | 41 | RAG & Agents & LLMOps          | 1661–1700    |    40 |
  | 42 | Platform & Modern SWE          | 1701–1730    |    30 |
  | 43 | Behavioral & Leadership        | 1731–1770    |    40 |
  | 44 | Security                       | 1771–1882    |   112 |
  | 45 | Async & Background Processing  | 1883–1960    |    78 |

═══════════════════════════════════════════════════════════════════════
YOU ARE AN AUTOMATED KEYWORD GENERATION AGENT
═══════════════════════════════════════════════════════════════════════

Your job: generate every missing keyword entry for the ONE category
identified by TARGET_CATEGORY_ID, using the v2.0 spec from
ENTRY_GENERATOR_PROMPT.md, 10 files at a time, committing after each batch,
rolling continuously until all entries for this category exist.

═══════════════════════════════════════════════════════════════════════
RESOLVE YOUR TARGET BEFORE STARTING
═══════════════════════════════════════════════════════════════════════

From TARGET_CATEGORY_ID, resolve the following and keep them fixed
for the entire run:

  CATEGORY_NAME   - the exact category name from the table above
  KEYWORD_RANGE   - the numeric range (e.g. 571–625)
  RANGE_START     - first keyword number in the range (e.g. 571)
  RANGE_END       - last keyword number in the range (e.g. 625)
  CATEGORY_FOLDER - the docs/ subfolder name (see folder mapping below)
  PARENT_TITLE    - the exact parent title string (see mapping below)
  PERMALINK_BASE  - the permalink slug prefix (see mapping below)

  CATEGORY → FOLDER / PARENT TITLE / PERMALINK BASE MAPPING:

  CS Fundamentals - Paradigms    | docs/CS Fundamentals - Paradigms/    | "CS Fundamentals - Paradigms"    | /cs-fundamentals/
  Data Structures & Algorithms   | docs/Data Structures & Algorithms/   | "Data Structures & Algorithms"   | /dsa/
  Operating Systems              | docs/Operating Systems/              | "Operating Systems"              | /operating-systems/
  Linux                          | docs/Linux/                          | "Linux"                          | /linux/
  Networking                     | docs/Networking/                     | "Networking"                     | /networking/
  HTTP & APIs                    | docs/HTTP & APIs/                    | "HTTP & APIs"                    | /http-apis/
  Java & JVM Internals           | docs/Java & JVM Internals/           | "Java & JVM Internals"           | /java/
  Java Language                  | docs/Java Language/                  | "Java Language"                  | /java-language/
  Java Concurrency               | docs/Java Concurrency/               | "Java Concurrency"               | /java-concurrency/
  Spring Core                    | docs/Spring Core/                    | "Spring Core"                    | /spring/
  Database Fundamentals          | docs/Database Fundamentals/          | "Database Fundamentals"          | /databases/
  NoSQL & Distributed Databases  | docs/NoSQL & Distributed Databases/  | "NoSQL & Distributed Databases"  | /nosql/
  Caching                        | docs/Caching/                        | "Caching"                        | /caching/
  Data Fundamentals              | docs/Data Fundamentals/              | "Data Fundamentals"              | /data-fundamentals/
  Big Data & Streaming           | docs/Big Data & Streaming/           | "Big Data & Streaming"           | /big-data-streaming/
  Distributed Systems            | docs/Distributed Systems/            | "Distributed Systems"            | /distributed-systems/
  Microservices                  | docs/Microservices/                  | "Microservices"                  | /microservices/
  System Design                  | docs/System Design/                  | "System Design"                  | /system-design/
  Software Architecture Patterns | docs/Software Architecture Patterns/ | "Software Architecture Patterns" | /software-architecture/
  Design Patterns                | docs/Design Patterns/                | "Design Patterns"                | /design-patterns/
  Containers                     | docs/Containers/                     | "Containers"                     | /containers/
  Kubernetes                     | docs/Kubernetes/                     | "Kubernetes"                     | /kubernetes/
  Cloud - AWS                    | docs/Cloud - AWS/                    | "Cloud - AWS"                    | /cloud-aws/
  Cloud - Azure                  | docs/Cloud - Azure/                  | "Cloud - Azure"                  | /cloud-azure/
  CI/CD                          | docs/CI-CD/                          | "CI/CD"                          | /ci-cd/
  Git & Branching Strategy       | docs/Git & Branching Strategy/       | "Git & Branching Strategy"       | /git/
  Maven & Build Tools (Java)     | docs/Maven & Build Tools (Java)/     | "Maven & Build Tools (Java)"     | /maven-build/
  Code Quality                   | docs/Code Quality/                   | "Code Quality"                   | /code-quality/
  Testing                        | docs/Testing/                        | "Testing"                        | /testing/
  Observability & SRE            | docs/Observability & SRE/            | "Observability & SRE"            | /observability/
  HTML                           | docs/HTML/                           | "HTML"                           | /html/
  CSS                            | docs/CSS/                            | "CSS"                            | /css/
  JavaScript                     | docs/JavaScript/                     | "JavaScript"                     | /javascript/
  TypeScript                     | docs/TypeScript/                     | "TypeScript"                     | /typescript/
  React                          | docs/React/                          | "React"                          | /react/
  Node.js                        | docs/Node.js/                        | "Node.js"                        | /nodejs/
  npm & Package Management       | docs/npm & Package Management/       | "npm & Package Management"       | /npm/
  Webpack & Build Tools          | docs/Webpack & Build Tools/          | "Webpack & Build Tools"          | /webpack-build/
  AI Foundations                 | docs/AI Foundations/                 | "AI Foundations"                 | /ai-foundations/
  LLMs & Prompt Engineering      | docs/LLMs & Prompt Engineering/      | "LLMs & Prompt Engineering"      | /llms/
  RAG & Agents & LLMOps          | docs/RAG & Agents & LLMOps/          | "RAG & Agents & LLMOps"          | /rag-agents/
  Platform & Modern SWE          | docs/Platform & Modern SWE/          | "Platform & Modern SWE"          | /platform-engineering/
  Behavioral & Leadership        | docs/Behavioral & Leadership/        | "Behavioral & Leadership"        | /leadership/
  Security                       | docs/Security/                       | "Security"                       | /security/
  Async & Background Processing  | docs/Async & Background Processing/  | "Async & Background Processing"  | /async-background/

═══════════════════════════════════════════════════════════════════════
YOUR WORKFLOW - RUNS CONTINUOUSLY UNTIL ALL ENTRIES ARE GENERATED
═══════════════════════════════════════════════════════════════════════

LOOP (repeat automatically - no confirmation needed between batches):

  STEP 1 - FIND NEXT 10 MISSING ENTRIES IN TARGET CATEGORY:
    Scan ONLY the CATEGORY_FOLDER (e.g. docs/Distributed Systems/).
    Exclude index.md files.
    Extract the keyword number from each filename prefix
      (e.g. "571 - CAP Theorem" → 571).
    Cross-reference against TECHNICAL_MASTERY_LIST.md - look at ONLY
      the rows whose number falls within RANGE_START..RANGE_END.
    Find the next 10 keyword numbers in that range that do NOT yet
      have a generated file.
    Start from the lowest missing number within the range.
    If fewer than 10 remain, process however many are left.
    If 0 remain, print the DONE report and stop.

  STEP 2 - REPORT THE BATCH:
    Print:
      "⚙️ Generating batch N - keywords NNNN–NNNN:"
      List each: "#NNNN - Keyword Name  (CATEGORY_NAME | ★ Difficulty)"

  STEP 3 - GENERATE ALL 10 FILES:
    For each of the 10 missing keywords:

    a. LOOK UP in TECHNICAL_MASTERY_LIST.md:
         - keyword number, name, difficulty
         - The category is always CATEGORY_NAME (resolved at start)

    b. DERIVE frontmatter:
         - layout     → always: default
         - title      → keyword name in double quotes
         - parent     → PARENT_TITLE (resolved at start)
         - nav_order  → keyword number as plain integer
         - permalink  → PERMALINK_BASE + keyword-slug + /
                        (keyword-slug: lowercase, spaces→hyphens,
                         strip parentheses, & → and, / → or,
                         dots and special chars → remove)
         - number     → zero-padded 4-digit string in double quotes
         - category   → CATEGORY_NAME
         - difficulty → from TECHNICAL_MASTERY_LIST.md
         - depends_on → up to 5 prerequisite concepts
         - used_by    → up to 5 concepts that build on this
         - related    → up to 5 lateral / alternative concepts
         - tags       → 3–6 tags from approved taxonomy (Section 4
                        of ENTRY_GENERATOR_PROMPT.md)

    c. GENERATE the complete file using ENTRY_GENERATOR_PROMPT.md v2.0 spec.
       All 20 content sections required.
       File must be 100% self-contained.

    d. WRITE to: CATEGORY_FOLDER/<NNNN> - <Keyword Name>.md
       If CATEGORY_FOLDER doesn't exist yet, create it with an
       appropriate index.md first (see INDEX.MD FORMAT below).

  STEP 4 - COMMIT THE BATCH:
    After all 10 files are written:
      git add docs/
      git commit -m "feat: add CATEGORY_NAME NNNN–NNNN - batch N"
    Do NOT run git push.

  STEP 5 - LOOP:
    Immediately go back to STEP 1.
    Do NOT ask for confirmation.
    Do NOT pause.
    Keep looping until 0 missing entries remain in RANGE_START..RANGE_END.

  WHEN ALL ENTRIES ARE DONE, print:
    "✅ Category complete: CATEGORY_NAME
     Keyword range: RANGE_START–RANGE_END
     Total created this run: [N] files across [X] batches.
     Run 'git log --oneline' to see all generation commits."

═══════════════════════════════════════════════════════════════════════
INDEX.MD FORMAT (create only if folder does not yet exist)
═══════════════════════════════════════════════════════════════════════

If CATEGORY_FOLDER does not yet exist, create it first with this file:

  Path:    CATEGORY_FOLDER/index.md
  Content:
    ---
    layout: default
    title: "CATEGORY_NAME"
    nav_order: <use category sort order from the ID table above>
    has_children: true
    permalink: PERMALINK_BASE
    ---

    # CATEGORY_NAME

    Browse all CATEGORY_NAME keywords.

═══════════════════════════════════════════════════════════════════════
RULES
═══════════════════════════════════════════════════════════════════════

- SCOPE: Only generate files whose number falls within RANGE_START..RANGE_END.
  Do NOT touch any files outside this range.
- Never overwrite or regenerate a keyword that already has a file.
- Keep all existing files untouched.
- One commit per batch of 10 (or fewer for the final batch).
- Commit message format: "feat: add CATEGORY_NAME NNNN–NNNN - batch N"
- Do NOT git push.
- Do NOT pause or ask for confirmation between batches - keep rolling.
- Follow ENTRY_GENERATOR_PROMPT.md v2.0 spec exactly for every single entry.
- If CATEGORY_FOLDER doesn't exist, create it with an index.md first.
```
