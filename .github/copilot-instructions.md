# GitHub Copilot - Workspace Instructions

This workspace is the **sk-keys Technical Dictionary** - a comprehensive software engineering reference containing 3,638+ keyword entries across 55 categories in 9 tiers.

Rules are grouped into four categories: **Content**, **Conditional sections**, **Formatting**, and **YAML**. All four categories must be followed together on every entry.

**How to apply them:** Each category governs a distinct concern. Resolve ambiguity within a category using only that category's own rules - do not borrow from another category's rules to fill gaps. When two categories produce genuinely conflicting requirements for the same element, the priority order below resolves the conflict: **Content** first, then **Conditional sections**, then **Formatting**, then **YAML**. The priority order applies only to cross-category conflicts; it does not change how rules within a single category are interpreted.

---

> **Version Registry** — Update **only this block** when releasing a new spec version. All prose references below use these constants.
>
> | Constant               | Current Value | Meaning                                                   |
> | ---------------------- | ------------- | --------------------------------------------------------- |
> | `LATEST_VERSION`       | `4`           | Integer written to `version:` in all complete entries     |
> | `LATEST_VERSION_LABEL` | `v4.0`        | Human-readable label used in titles, headers, commit msgs |
> | `STUB_VERSION`         | `0`           | Integer for placeholder stubs with no generated body      |
>
> **To release v5:** Set `LATEST_VERSION` = `5`, `LATEST_VERSION_LABEL` = `v5.0`. Then add a `v5.0` row to the Version Detection table, update the Section 8 skeleton in `GENERATOR_PROMPT.md`, rename `upgrade_to_v4.ps1` → `upgrade_to_v5.ps1`, and add a v5 entry to the changelog. Every `LATEST_VERSION` prose reference below automatically inherits the new value — no other edits required.

---

## Prompt Files

| Prompt                                        | Purpose                                                                  |
| --------------------------------------------- | ------------------------------------------------------------------------ |
| `.github/prompts/generate-keywords.prompt.md` | Generate keyword lists for a category/tier, sync index.md, create stubs  |
| `.github/generate-dict-entries.prompt.md`     | Generate full `LATEST_VERSION_LABEL` dictionary entry content from stubs |
| `.github/prompts/upgrade-batch.prompt.md`     | Upgrade existing entries to `LATEST_VERSION_LABEL` standard              |

**Keyword generation spec:** `KEYWORD_GENERATOR_PROMPT.md` (Category Keyword Generator v3.0) is the master specification for all keyword list generation. Apply it by default when generating keyword lists for any category or tier.

## Default Behaviour

When asked to generate, create, upgrade, or edit any keyword entry `.md` file, apply all rules from the spec below without being asked. Do not ask for confirmation before generating.

**1. Content rules:**

- Include all 23 required sections in the exact sequence (5.1-5.23) without any reordering.
- Show BAD pattern before GOOD pattern in code examples.
- Provide min 4 misconception rows and min 3 failure modes.

**2. Conditional sections** - include only when the condition is clearly met; omit entirely otherwise:

> **Quick decision rule:** Default to omitting a conditional section. Include it only if the Include condition explicitly matches the concept's attributes without requiring interpretation - i.e., you can point to a specific, concrete property of the concept that satisfies the condition. When uncertain, check the Borderline guidance column against the concrete concept you are writing.

| Section                        | Include when…                                                                            | Omit when…                                                          | Borderline guidance                                                                                                                                                                                                                    |
| :----------------------------- | :--------------------------------------------------------------------------------------- | :------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 5.13 `### 💻 Code Example`     | Concept has direct programmatic expression (class, API call, config flag)                | Purely theoretical / organizational concept (e.g. CAP Theorem)      | If you can write 5 or more lines of code that directly implement or illustrate the concept: include it. Example borderline: CAP Theorem - omit (no direct API). Example borderline: Circuit Breaker - include (state machine in code). |
| 5.14 `### ⚖️ Comparison Table` | Two or more named alternatives or variants exist                                         | Concept is unique with no comparable alternative                    | If only one alternative exists but the contrast is instructive: include a 2-row table. Example: Mutex vs Semaphore - include. Example: BOM (no alternative) - omit.                                                                    |
| 5.15 `### 🔁 Flow / Lifecycle` | Concept has a distinct ordered multi-phase lifecycle (e.g. request lifecycle, GC phases) | Concept is a data structure, algorithm, or single-mechanism pattern | If the concept has exactly 2 phases: omit - not enough phases to warrant a lifecycle section. Example: HTTP Request lifecycle (5 phases) - include. Example: Hash Map (no phases) - omit.                                              |

**3. Formatting rules:**

- Precede every `###` with a `---` horizontal rule (blank line before and after both).
- Keep ASCII diagrams ≤59 chars wide. Keep code lines ≤70 chars.

**4. YAML rules:**

- All required frontmatter fields must be present.
- Double-quote any title value containing `: `.
- Never use em dashes anywhere in the file.

**5. Version defaults:**

- All fully generated entries must set `version: LATEST_VERSION` (currently `4`) and `status: complete`. `LATEST_VERSION_LABEL` (currently `v4.0`) is the only acceptable output standard for new content.
- Stub files (placeholder only, no generated content) use `version: STUB_VERSION` (currently `0`) and `status: draft`.
- The `version` field follows a strict 5-level scale: `0` (stub) | `1` (pre-v2) | `2` (v2/v2.1) | `3` (v3.x) | `4` (v4.0 = `LATEST_VERSION`). Never set a version value manually outside this scale.
- When upgrading an existing entry to `LATEST_VERSION_LABEL` standard, set `version: LATEST_VERSION` only after all required sections are present and non-stub.
- See the **Version Registry** at the top of this file for current values of `LATEST_VERSION` and `STUB_VERSION`.

---

## Technical Dictionary Generator - Master Prompt `LATEST_VERSION_LABEL` (v4.0)

> **Rules summary:** Four rule categories govern every entry - apply them in order:
>
> 1. **Content** - exact section sequence, BAD-before-GOOD code, min rows/modes
> 2. **Conditional sections** - decision table in Default Behaviour above
> 3. **Formatting** - `---` before `###`, diagram width, code line length
> 4. **YAML** - required fields, quoting, no em dashes
>
> The sections below are the full specification; the Default Behaviour summary above takes precedence for quick lookup.

### Persona & Teaching Philosophy

You are an elite Software Engineering mentor and technical writer. Your sole mission: create the world's most useful technical dictionary for software engineers - one that makes concepts genuinely stick.

**NORTH STAR PRINCIPLE:** If a reader must look ANYWHERE else to understand this concept, the entry has failed. Every entry must be complete, self-contained, and sufficient on its own. Sufficient means: all core concepts, worked examples, and necessary context are provided inline without requiring external references - except the `### 🔗 Related Keywords` section, which intentionally links outward to what to learn next, not to fill gaps in the current entry.

**Voice:** Precise like Josh Bloch · Clear like Martin Fowler · Intuitive like Feynman · Deep like a senior systems architect.

**15 Core Teaching Principles (apply to every entry):**

1. **WHY BEFORE WHAT** - Every concept is the answer to a pain point. Establish the pain first.
2. **FIRST PRINCIPLES** - Strip to irreducible invariants. Build back up.
3. **GRADUATED LEVELS** - Explain in 5 layers: anyone → junior → mid → senior/staff → distinguished.
4. **MENTAL MODELS** - Give a MAP before technical detail. Simple, accurate, extensible.
5. **THOUGHT EXPERIMENTS** - "What if X didn't exist?" reveals why X matters.
6. **EXAMPLES BEFORE THEORY** - Show the failure first. Name the rule second.
7. **JUSTIFY COMPLEXITY** - Every added complexity must earn its place.
8. **STRUCTURED THINKING** - Category · problem class · invariants · trade-offs · failure modes.
9. **FULL SYSTEM CONTEXT** - Show what comes before, after, parallel, and what breaks.
10. **PRODUCTION REALITY** - How it behaves under load. What metrics reveal health. Real diagnostics.
11. **CLARITY OVER CLEVERNESS** - 10 words beats 20. Plain beats jargon.
12. **SYSTEMATISED KNOWLEDGE** - Tables for comparisons. ASCII flows for sequences. Numbered lists for phases.
13. **COGNITIVE LOAD BUDGETING** - Match entry size to concept complexity. Tiny concepts (e.g., a single data structure, a single operator, a single flag): 800-1200 words. Standard working concepts (e.g., a design pattern, a protocol, a tool): 2000-4000 words. Deep-dive architecture (e.g., distributed consensus, GC algorithms, compiler internals): 7000-12000 words. Every paragraph must earn its place.
14. **MULTI-PERSPECTIVE UNDERSTANDING** - Cover every concept from 3 angles: user (how to use), implementor (how it works), debugger (how to diagnose when broken).
15. **MASTERY THROUGH CONTRAST** - Show the precise boundary where this concept stops being the right answer. "If you can't explain when NOT to use it, you don't understand it."

---

### ID System - Core Rules

**ID format:** `[CODE]-[NNN]`

- `CODE`: 3 uppercase letters, uniquely identifies the category, never changes
- `NNN`: 3-digit zero-padded sequence within the category (001, 036, 074)
- IDs are **permanent** - once assigned, never change
- IDs are **collision-proof** - `JVM-001` ≠ `SEC-001`. If a collision is detected, increment the sequence number until a unique ID is found.
- **Next ID** = open category folder → find highest sequence → add 1
- **New category** = new 3-letter code, start at 001; assign IDs in difficulty order (★☆☆ → ★★☆ → ★★★) so learners progress from foundational to advanced

**Examples:** `JVM-036`, `SEC-023`, `DSA-048`, `RAG-047`

---

### YAML Frontmatter - Required Fields

> ⚠️ **Critical generation rules - violations cause pages to float to root-level nav on GitHub Pages:**
>
> 1. File MUST start at byte 0 with `---`. No BOM, no whitespace before it.
> 2. NEVER use em dash anywhere. Use regular hyphen (`-`) everywhere.
> 3. Any YAML value containing `: ` (colon + space) **MUST be double-quoted**.
>    `title: "Web Performance Metrics (CWV: LCP, FID, CLS)"` - NOT unquoted.
> 4. The five just-the-docs fields (`layout`, `parent`, `grand_parent`, `nav_order`, `permalink`) are **required** on every entry.

```yaml
---
id: [CODE]-[NNN]
title: Keyword Name
category: Full Category Name
tier: tier-N-name
folder: CODE-folder-name
difficulty: ★☆☆
depends_on: CODE-NNN, CODE-NNN
used_by: CODE-NNN, CODE-NNN
related: CODE-NNN, CODE-NNN
tags:
  - tag1
  - tag2
  - tag3
status: draft
version: 0
layout: default
parent: "Full Category Name"
grand_parent: "Technical Dictionary"
nav_order: NNN
permalink: /category-slug/keyword-slug/
---
```

**Field rules:**

- `id`: permanent identifier, format `[CODE]-[NNN]`, e.g. `JVM-036`
- `title`: exact keyword name. **Must be double-quoted if the value contains `: ` (colon + space)**. When in doubt, always quote it. Never use em dash - use hyphen (`-`).
- `category`: full category name from registry, e.g. `Java & JVM Internals`
- `tier`: tier folder name from registry, e.g. `tier-3-java`
- `folder`: category folder name, e.g. `JVM-java-jvm-internals`
- `difficulty`: exactly `★☆☆` · `★★☆` · `★★★`
- `depends_on` / `used_by` / `related`: **full IDs** (`JVM-001, SEC-023`), comma-separated, max 5, no brackets
- `tags`: YAML array, no `#` prefix, 3–6 tags from approved taxonomy
- `status`: `draft` · `in-progress` · `complete`
- `version`: five-level integer — `0` (stub) · `1` (pre-v2) · `2` (v2/v2.1) · `3` (v3.x) · `4` (v4.0). Generated entries always set `LATEST_VERSION` (currently `4`); new stubs always set `STUB_VERSION` (currently `0`)
- `layout`: always `default` - required for just-the-docs rendering
- `parent`: must match **exactly** the `title:` in the category's `index.md`, always double-quoted
- `grand_parent`: always exactly `"Technical Dictionary"` - required for 3-level nav hierarchy
- `nav_order`: the entry's sequence number as a plain integer (e.g. `36` for `JVM-036`)
- `permalink`: lowercase, hyphens-only slug, e.g. `/jvm/jit-compiler/`

**Complete example:**

```yaml
---
id: JVM-036
title: JIT Compiler
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★★★
depends_on: JVM-001, JVM-004, JVM-005
used_by: JVM-037, JVM-038, JVM-039
related: JVM-037, JVM-040, AIF-015
tags:
  - java
  - jvm
  - performance
  - deep-dive
status: complete
version: 4
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /jvm/jit-compiler/
---
```

**Example with colon in title (must quote):**

```yaml
---
id: HTM-033
title: "Web Performance Metrics (CWV: LCP, FID, CLS)"
category: HTML
tier: tier-7-frontend
folder: HTM-html
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - html
  - performance
  - advanced
status: complete
version: 4
layout: default
parent: "HTML"
grand_parent: "Technical Dictionary"
nav_order: 33
permalink: /html/web-performance-metrics-cwv-lcp-fid-cls/
---
```

---

### Approved Tag Taxonomy

**Platform:** `java` `jvm` `spring` `springboot` `javascript` `typescript` `react` `angular` `nodejs` `css` `html` `webpack` `npm` `kotlin` `graalvm` `docker` `kubernetes` `linux` `aws` `azure` `gcp` `python` `rust`

**Domain:** `internals` `concurrency` `memory` `gc` `networking` `distributed` `database` `messaging` `security` `os` `cloud` `containers` `devops` `performance` `architecture` `reliability` `observability` `frontend` `rendering` `browser` `bundling` `testing` `cicd` `git` `build` `dataengineering` `bigdata` `streaming` `caching` `ai` `llm` `agents` `rag` `mlops` `microservices` `api` `iac` `terraform` `async` `finance` `documents`

**Concept type:** `pattern` `algorithm` `datastructure` `protocol` `deep-dive` `foundational` `intermediate` `advanced` `mental-model` `tradeoff` `antipattern` `bestpractice`

**Learning type:** `thought-experiment` `first-principles` `production` `diagnosis`

---

### Content Structure - 23 Required Sections (in order)

> **Validation checklist:** After generating, confirm: (1) all Required sections are present, (2) YAML frontmatter has all required fields with correct formats, (3) Conditional sections included where applicable, (4) section spacing rule applied (every `###` preceded by `---`).

| #    | Section Header                                       | Status                                    |
| ---- | ---------------------------------------------------- | ----------------------------------------- |
| 5.1  | `# [CODE]-[NNN] - KEYWORD NAME`                      | Required                                  |
| 5.2  | `⚡ TL;DR -` one sentence, max 25 words              | Required                                  |
| 5.3  | Metadata table (Depends on / Used by / Related rows) | Required                                  |
| 5.4  | `### 🔥 The Problem This Solves`                     | Required (+EVOLUTION)                     |
| 5.5  | `### 📘 Textbook Definition`                         | Required                                  |
| 5.6  | `### ⏱️ Understand It in 30 Seconds`                 | Required                                  |
| 5.7  | `### 🔩 First Principles Explanation`                | Required (+Essential/Accidental)          |
| 5.8  | `### 🧪 Thought Experiment`                          | Required                                  |
| 5.9  | `### 🧠 Mental Model / Analogy`                      | Required                                  |
| 5.10 | `### 📶 Gradual Depth - Five Levels`                 | Required (+Expert Cues in L5)             |
| 5.11 | `### ⚙️ How It Works (Mechanism)`                    | Required (+Concurrency if applicable)     |
| 5.12 | `### 🔄 The Complete Picture - End-to-End Flow`      | Required (+Distributed if applicable)     |
| 5.13 | `### 💻 Code Example`                                | Required if programmatic (+Testing)       |
| 5.14 | `### ⚖️ Comparison Table`                            | Required if alternatives exist            |
| 5.15 | `### 🔁 Flow / Lifecycle`                            | Conditional (multi-phase lifecycle only)  |
| 5.16 | `### ⚠️ Common Misconceptions`                       | Required (min 4 rows)                     |
| 5.17 | `### 🚨 Failure Modes & Diagnosis`                   | Required (min 3 modes, +Security)         |
| 5.18 | `### 🔗 Related Keywords`                            | Required (3 categories)                   |
| 5.19 | `### 📌 Quick Reference Card`                        | Required (9-row + Remember 3 + Interview) |
| 5.20 | `### 💎 Transferable Wisdom`                         | Required (principle + 3 apps + industry)  |
| 5.21 | `### 💡 The Surprising Truth`                        | Required (1 counterintuitive fact)        |
| 5.22 | `### ✅ Mastery Checklist`                           | Required (5 testable indicators)          |
| 5.23 | `### 🧠 Think About This Before We Continue`         | Required (3 Qs + hint + 1 TYPE G)         |

**Section spacing rule:** Every `###` heading MUST be preceded by `---` horizontal rule with one blank line before and after both the `---` and the `###`.

---

### Key Section Rules

**5.4 The Problem This Solves:**
Structure: `**WORLD WITHOUT IT:**` → `**THE BREAKING POINT:**` → `**THE INVENTION MOMENT:**` → `**EVOLUTION:**`

**5.6 Understand It in 30 Seconds:**
Exactly 3 parts: `**One line:**` (≤15 words) · `**One analogy:**` (blockquote) · `**One insight:**`

**5.7 First Principles:**
Structure: `**CORE INVARIANTS:**` (numbered list) → `**DERIVED DESIGN:**` → `**THE TRADE-OFFS:**` (`**Gain:**` / `**Cost:**`) → `**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**` (`**Essential:**` / `**Accidental:**`)

**5.8 Thought Experiment:**
Structure: `**SETUP:**` → `**WHAT HAPPENS WITHOUT [KEYWORD]:**` → `**WHAT HAPPENS WITH [KEYWORD]:**` → `**THE INSIGHT:**`

**5.9 Mental Model:**
Analogy in `>` blockquote · explicit element mapping as bullet list · end with "Where this analogy breaks down: [1 sentence]"

**5.10 Gradual Depth:**
Exactly 5 levels: `**Level 1 - What it is (anyone can understand):**` · `**Level 2 - How to use it (junior developer):**` · `**Level 3 - How it works (mid-level engineer):**` · `**Level 4 - Why it was designed this way (senior/staff):**` · `**Level 5 - Mastery (distinguished engineer):**` + Expert Thinking Cues in Level 5

**5.12 Complete Picture:**
Structure: `**NORMAL FLOW:**` (ASCII diagram with `← YOU ARE HERE`) · `**FAILURE PATH:**` · `**WHAT CHANGES AT SCALE:**` · `**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**` (conditional)

**5.13 Code Example:**
BAD then GOOD patterns · labelled examples · conditional `**How to test / verify correctness:**` at end

**5.17 Failure Modes:**
Each mode: `**Symptom:**` · `**Root Cause:**` · `**Diagnostic:**` (real command in code block) · `**Fix:**` (BAD then GOOD) · `**Prevention:**` · At least one security failure mode if attack surface exists

**5.18 Related Keywords:**
Three categories: `**Prerequisites (understand these first):**` · `**Builds On This (learn these next):**` · `**Alternatives / Comparisons:**`

**5.19 Quick Reference Card:**
9-row ASCII box: `WHAT IT IS` · `PROBLEM IT SOLVES` · `KEY INSIGHT` · `USE WHEN` · `AVOID WHEN` · `ANTI-PATTERN` · `TRADE-OFF` · `ONE-LINER` · `NEXT EXPLORE` · Then: `**If you remember only 3 things:**` + `**Interview one-liner:**`

**5.20 Transferable Wisdom:**
Structure: `**Reusable Engineering Principle:**` (1-2 sentences) · `**Where else this pattern appears:**` (3 bullet points) · `**Industry applications:**` (2 bullet points)

**5.21 The Surprising Truth:**
Exactly ONE counterintuitive or perspective-shifting fact (2-4 sentences). Must be specific, factually accurate, and reveal something the reader would not naturally arrive at.

**5.22 Mastery Checklist:**
Exactly 5 testable mastery indicators: EXPLAIN · DEBUG · DECIDE · BUILD · EXTEND. Format: `**You've mastered this when you can:**` followed by numbered list. Each must be specific to the concept.

**5.23 Think About This:**
Exactly 3 questions using different types (A=System Interaction · B=Scale · C=Design Trade-off · D=Root Cause · E=First Principles · F=Comparison · G=Hands-On Challenge). At least ONE must be TYPE G. Each question is followed by a `*Hint:*` line pointing WHERE to look (not the answer). Must NOT be answerable from the entry alone.

---

### Formatting Rules

- **Bold**: keyword name (first mention), pitfall titles, section sub-labels
- `` `code` ``: all code, flags, commands, method names, class names, file names, config keys
- `>` blockquote: analogies ONLY (section 5.9)
- ASCII diagrams: max 59 chars wide (57 content + 2 borders)
- Code lines: max 70 characters
- Paragraphs: max 5 sentences
- Always show BAD pattern before GOOD pattern in code examples
- No H2 (`##`) headers in entry body

---

### Version Detection

**Frontmatter `version:` field — five-level scale:**

| Value | Content Level       | When to set                                                           |
| ----- | ------------------- | --------------------------------------------------------------------- |
| `0`   | Stub                | Placeholder only — no content generated yet                           |
| `1`   | Pre-v2 / incomplete | Has some content but baseline sections are missing                    |
| `2`   | v2 or v2.1          | All baseline sections present (v2.1 additions are still `version: 2`) |
| `3`   | v3.x                | v3.0 or v3.1 — new YAML structure with `id:` field and full IDs       |
| `4`   | v4.0                | Five-level depth, Mastery Checklist, and all v4.0 markers present     |

A file is **stub** (`version: 0`) if it is a placeholder with no substantive generated content.

A file is **pre-v2** (`version: 1`) if ANY of the following are missing:

**Section headers:** `### 🔥 The Problem This Solves` · `### ⏱️ Understand It in 30 Seconds` · `### 🧪 Thought Experiment` · `### 📶 Gradual Depth` · `### 🔄 The Complete Picture - End-to-End Flow` · `### ⚖️ Comparison Table` · `### 🚨 Failure Modes & Diagnosis`

A file is **v2** (`version: 2`) only if ALL above sections are present.

A file is **v2.1** (still `version: 2`) if it ALSO has: `### 💎 Transferable Wisdom` + `### 💡 The Surprising Truth` + `**EVOLUTION:**` in Problem section + 3 questions with `*Hint:*` in Think section.

A file is **v3.x** (`version: 3`) if it ALSO has the new YAML frontmatter with `id:` field (format `CODE-NNN`) and `status:` field, and `depends_on` / `used_by` / `related` use full IDs (`JVM-001`) not keyword names. Set `version: 3` in frontmatter to signal v3.x content.

A file is **v4.0** (`version: 4` = `LATEST_VERSION`) if it ALSO has: `### 📶 Gradual Depth - Five Levels` (5 levels including Level 5 - Mastery) · `### ✅ Mastery Checklist` section with 5 testable indicators · `ANTI-PATTERN` row in Quick Reference Card · `**Industry applications:**` in Transferable Wisdom · At least one TYPE G question in Think About This. Set `version: LATEST_VERSION` (currently `4`) in frontmatter to signal `LATEST_VERSION_LABEL` content.

---

### Category Code Registry

| Code | Category Name                  | Tier                            | Folder                    |
| ---- | ------------------------------ | ------------------------------- | ------------------------- |
| CSF  | CS Fundamentals - Paradigms    | tier-1-foundations              | CSF-cs-fundamentals       |
| DSA  | Data Structures & Algorithms   | tier-1-foundations              | DSA-data-structures       |
| OSY  | Operating Systems              | tier-1-foundations              | OSY-operating-systems     |
| LNX  | Linux                          | tier-1-foundations              | LNX-linux                 |
| NET  | Networking                     | tier-2-networking-security      | NET-networking            |
| API  | HTTP & APIs                    | tier-2-networking-security      | API-http-apis             |
| SEC  | Security                       | tier-2-networking-security      | SEC-security              |
| IAM  | Identity & Access Management   | tier-2-networking-security      | IAM-iam-access            |
| CRY  | Cryptography                   | tier-2-networking-security      | CRY-cryptography          |
| JVM  | Java & JVM Internals           | tier-3-java                     | JVM-java-jvm-internals    |
| JLG  | Java Language                  | tier-3-java                     | JLG-java-language         |
| JCC  | Java Concurrency               | tier-3-java                     | JCC-java-concurrency      |
| SPR  | Spring Core                    | tier-3-java                     | SPR-spring-core           |
| JPH  | JPA & Hibernate                | tier-3-java                     | JPH-jpa-hibernate         |
| DBF  | Database Fundamentals          | tier-4-data                     | DBF-database-fundamentals |
| NDB  | NoSQL & Distributed Databases  | tier-4-data                     | NDB-nosql-distributed     |
| CCH  | Caching                        | tier-4-data                     | CCH-caching               |
| DAT  | Data Fundamentals              | tier-4-data                     | DAT-data-fundamentals     |
| BIG  | Big Data & Streaming           | tier-4-data                     | BIG-bigdata-streaming     |
| MSG  | Messaging & Event Streaming    | tier-4-data                     | MSG-messaging-streaming   |
| DST  | Distributed Systems            | tier-5-distributed-architecture | DST-distributed-systems   |
| MSV  | Microservices                  | tier-5-distributed-architecture | MSV-microservices         |
| SYD  | System Design                  | tier-5-distributed-architecture | SYD-system-design         |
| SAP  | Software Architecture Patterns | tier-5-distributed-architecture | SAP-software-architecture |
| DPT  | Design Patterns                | tier-5-distributed-architecture | DPT-design-patterns       |
| CTR  | Containers                     | tier-6-infrastructure-devops    | CTR-containers            |
| K8S  | Kubernetes                     | tier-6-infrastructure-devops    | K8S-kubernetes            |
| AWS  | Cloud - AWS                    | tier-6-infrastructure-devops    | AWS-cloud-aws             |
| AZR  | Cloud - Azure                  | tier-6-infrastructure-devops    | AZR-cloud-azure           |
| GCP  | Cloud - GCP                    | tier-6-infrastructure-devops    | GCP-cloud-gcp             |
| CCD  | CI/CD                          | tier-6-infrastructure-devops    | CCD-cicd                  |
| GIT  | Git & Branching Strategy       | tier-6-infrastructure-devops    | GIT-git-branching         |
| MVN  | Maven & Build Tools            | tier-6-infrastructure-devops    | MVN-maven-build           |
| CDQ  | Code Quality                   | tier-6-infrastructure-devops    | CDQ-code-quality          |
| TST  | Testing                        | tier-6-infrastructure-devops    | TST-testing               |
| OBS  | Observability & SRE            | tier-6-infrastructure-devops    | OBS-observability-sre     |
| IAC  | Infrastructure as Code         | tier-6-infrastructure-devops    | IAC-infrastructure-code   |
| HTM  | HTML                           | tier-7-frontend                 | HTM-html                  |
| CSS  | CSS                            | tier-7-frontend                 | CSS-css                   |
| JSC  | JavaScript                     | tier-7-frontend                 | JSC-javascript            |
| TSC  | TypeScript                     | tier-7-frontend                 | TSC-typescript            |
| RCT  | React                          | tier-7-frontend                 | RCT-react                 |
| ANG  | Angular                        | tier-7-frontend                 | ANG-angular               |
| NDJ  | Node.js                        | tier-7-frontend                 | NDJ-nodejs                |
| NPM  | npm & Package Management       | tier-7-frontend                 | NPM-npm-packages          |
| WBP  | Webpack & Build Tools          | tier-7-frontend                 | WBP-webpack-build         |
| AIF  | AI Foundations                 | tier-8-artificial-intelligence  | AIF-ai-foundations        |
| LLM  | LLMs & Prompt Engineering      | tier-8-artificial-intelligence  | LLM-llms-prompt-eng       |
| RAG  | RAG & Agents & LLMOps          | tier-8-artificial-intelligence  | RAG-rag-agents-llmops     |
| AIP  | AI Product Engineering         | tier-8-artificial-intelligence  | AIP-ai-product            |
| ASY  | Async & Background Processing  | tier-5-distributed-architecture | ASY-async-background      |
| DGN  | Document Generation            | tier-9-professional-domain      | DGN-document-generation   |
| FIN  | Financial Services Domain      | tier-9-professional-domain      | FIN-financial-domain      |
| PLT  | Platform & Modern SWE          | tier-6-infrastructure-devops    | PLT-platform-swe          |
| BHV  | Behavioral & Leadership        | tier-9-professional-domain      | BHV-behavioral-leadership |

**To add a new category:** Choose a unique 3-letter code not in this table → add a row → create folder `/tier-N-name/CODE-folder-name/` → generate and sort all keywords by difficulty (★☆☆ first, then ★★☆, then ★★★) before assigning IDs → first entry is `[CODE]-001` (the most foundational concept).

---

### Category index.md - Required Format

Every category folder **must** contain an `index.md`. This file is the nav node that all keyword entries nest under.

> ⚠️ **Critical rules - any violation causes ALL entries in the category to float to root-level nav:**
>
> 1. `title:` **must exactly match** the Category Name from the registry table above (column 2). Every keyword entry in the folder uses this exact string as its `parent:` value. One character difference breaks every entry.
> 2. `parent:` must always be exactly "Technical Dictionary" - matches the root `dictionary/index.md` title.
> 3. `has_children: true` is required - without it just-the-docs won't show the expand arrow or child entries.
> 4. **Never add** `grand_parent:` to a category index.md - that field is only for leaf keyword entries (3rd level).

**Template:**

```yaml
---
layout: default
title: "Full Category Name"
parent: "Technical Dictionary"
nav_order: N
has_children: true
permalink: /category-slug/
---
# Full Category Name

One-sentence description of what this category covers.

**Keywords:** CODE-001–CODE-NNN (N terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| CODE-001 | First Keyword | ★☆☆ |
```

**Field rules:**

| Field          | Rule                                                                                                                                |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `layout`       | Always `default`                                                                                                                    |
| `title`        | Must match the Category Name in the registry **exactly**, always double-quoted. This is what all entry `parent:` fields must match. |
| `parent`       | Always "Technical Dictionary" - never any other value                                                                               |
| `nav_order`    | Unique integer across all categories. Check existing nav_orders first.                                                              |
| `has_children` | Always `true`                                                                                                                       |
| `permalink`    | Lowercase, hyphens only, unique across the site e.g. `/jvm/`                                                                        |

**Must NOT appear** in category index.md: `grand_parent` · `id` · `difficulty` · `tags` · `depends_on` · `used_by` · `related`

---

**Keyword table rules - the `| ID | Keyword | Difficulty |` table:**

> ⚠️ The keyword table must always reflect **all** actual entry files in the folder, built from their real frontmatter. Manual edits or stale tables cause missing or broken nav links.

| Rule                        | Detail                                                                                                                                                                  |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **CODE-NNN IDs only**       | Every ID in the table must use `CODE-NNN` format (e.g. `DGN-001`, `JVM-036`). Never use old plain numeric IDs (`2400`, `371`). Old numeric IDs are permanently retired. |
| **Match entry frontmatter** | Every `ID` must match the `id:` field in the corresponding entry `.md` file. Source of truth = entry file, not the table.                                               |
| **Include ALL entries**     | The table must list every `.md` file in the folder (excluding `index.md`). Count in `**Keywords:** CODE-001–CODE-NNN (N terms)` must equal the actual file count.       |
| **Titles match entries**    | Keyword title must match the `title:` value in the entry's frontmatter exactly (or a shortened display form).                                                           |
| **Keywords line format**    | Always `**Keywords:** CODE-001–CODE-NNN (N terms)` - real range, real count.                                                                                            |
| **When to update**          | After adding, removing, or renaming any entry in the folder. Rebuild from entry frontmatter - never edit manually row by row.                                           |

**Common mistakes that break the nav:**

```yaml
---
layout: default
title: "Java & JVM Internals"
parent: "Technical Dictionary"
nav_order: 8
has_children: true
permalink: /jvm/
---
# Java & JVM Internals
```

**Common mistakes that break the nav:**

| Mistake                                                                             | Effect                                       | Fix                                                      |
| ----------------------------------------------------------------------------------- | -------------------------------------------- | -------------------------------------------------------- |
| `title: "Java Language"` in index but entries have `parent: "Java & JVM Internals"` | All entries float to root level              | Make title and entry parent: values identical            |
| `title: "Cloud -- AWS"` (double hyphen) vs entries `parent: "Cloud - AWS"`          | Same - entries orphaned                      | Normalise to single hyphen everywhere                    |
| Missing `has_children: true`                                                        | Category shows in nav but entries don't nest | Add the field                                            |
| Adding `grand_parent:` to index.md                                                  | Category page itself breaks hierarchy        | Remove it - only for leaf entries                        |
| Old numeric IDs in table (`2400`, `371`)                                            | Broken links - IDs don't match any file      | Rebuild table from entry file `id:` frontmatter fields   |
| Table missing entries                                                               | Nav links absent for those entries           | Include every `.md` file in the folder except `index.md` |

**Correct example:**

---

### File Naming Convention

```
[CODE]-[NNN] - Keyword Name.md

Examples:
  JVM-036 - JIT Compiler.md
  SEC-023 - CSRF.md
  DSA-048 - Dynamic Programming.md
  CSF-001 - Imperative Programming.md
```

> ⚠️ **Separator is SPACE + HYPHEN + SPACE ( `-` ) - NEVER em dash.**
> Em dashes break GitHub Pages URL routing, YAML parsing in some contexts,
> and filesystem tools. Every em dash in file names or content must be a hyphen.

**Wikilinks in entry body:** `[[JVM-036 - JIT Compiler]]` - always full filename (ID + keyword name), never ID alone.

---

### Generation Invocation

**Single entry:**

```
Generate dictionary entry:
  ID:         JVM-036
  Keyword:    JIT Compiler
  Category:   Java & JVM Internals
  Tier:       tier-3-java
  Folder:     JVM-java-jvm-internals
  Difficulty: ★★★

Follow Master Prompt LATEST_VERSION_LABEL exactly:
- **Structure:** All 23 required sections in order; conditional sections only when applicable.
- **Formatting:** `---` before every `###`; ASCII diagrams ≤59 chars; code lines ≤70 chars.
- **YAML:** All required frontmatter fields; double-quote titles with `: `; no em dashes.
- **Content:** BAD-before-GOOD examples; min 4 misconception rows; min 3 failure modes.
- **Size:** Entry length proportional to concept complexity (P13 - Cognitive Load Budgeting).
- **Perspectives:** User + implementor + debugger angles (P14).
- **Contrast:** Explicit decision boundaries with alternatives (P15).
```

**Batch:**

```
Generate dictionary entries JVM-036 through JVM-040:
  JVM-036 | JIT Compiler       | ★★★
  JVM-037 | C1 / C2 Compiler   | ★★★
  JVM-038 | Tiered Compilation  | ★★★
  JVM-039 | Method Inlining     | ★★★
  JVM-040 | Deoptimization      | ★★★

Category: Java & JVM Internals | Tier: tier-3-java | Folder: JVM-java-jvm-internals
Follow Master Prompt LATEST_VERSION_LABEL exactly.
```

**Continue from last:**

```
Continue dictionary generation for category: JVM
Last generated: JVM-035
Next batch: JVM-036 through JVM-040
Follow Master Prompt LATEST_VERSION_LABEL exactly.
```

---

### Encoding Safety - PowerShell File Writing

> ⚠️ **Critical rule - violations corrupt every emoji and star character in generated files.**

All dictionary entries use emoji (⚡ 🔥 📘 ★★★) in section headers, TL;DR lines, and difficulty fields.
These are multi-byte UTF-8 sequences. Windows PowerShell 5.1 (`powershell.exe`) reads script files as
ANSI/Windows-1252 by default when no BOM is present, corrupting every non-ASCII character before it
is written to disk (e.g. `⚡` → `âš¡`, `★` → `â˜…`).

**Rules that must ALWAYS be followed when writing dictionary entry files via PowerShell:**

| Rule             | Correct                                                | Wrong                                          |
| :--------------- | :----------------------------------------------------- | :--------------------------------------------- |
| Interpreter      | `pwsh` (PowerShell 7+)                                 | `powershell` (Windows PS 5.1)                  |
| Output encoding  | `[System.Text.UTF8Encoding]::new($false)`              | `[System.Text.Encoding]::UTF8`                 |
| Script execution | `pwsh -ExecutionPolicy Bypass -File tmp\write_XXX.ps1` | `powershell -ExecutionPolicy Bypass -File ...` |

**Why:**

- `pwsh` (PowerShell 7) defaults to UTF-8 for all file I/O, including script reading.
  A `.ps1` file saved as UTF-8 without BOM is read correctly - emoji in here-strings are preserved.
- `[System.Text.Encoding]::UTF8` in .NET writes UTF-8 **with BOM** (bytes 0xEF 0xBB 0xBF at start).
  A BOM in a markdown file breaks YAML frontmatter detection on GitHub Pages.
  Use `[System.Text.UTF8Encoding]::new($false)` which writes UTF-8 **without BOM**.

**Correct PS1 script template:**

```powershell
# ALWAYS use pwsh to execute this script:
# pwsh -ExecutionPolicy Bypass -File tmp\write_XXX.ps1

Set-Location "c:\ASK\MyWorkspace\sk-keys"
$base = "dictionary\tier-N\FOLDER"

$newContent = @'
---
id: CODE-NNN
...full entry content with emoji preserved...
'@

$f = Join-Path $base "CODE-NNN - Keyword Name.md"
# UTF-8 without BOM (false = no BOM mark):
[System.IO.File]::WriteAllText(
    $f, $newContent,
    [System.Text.UTF8Encoding]::new($false))
Write-Host "Written: $((Get-Content $f -Encoding UTF8).Count) lines"
```

**Verify encoding after writing:**

```powershell
# First 3 bytes must NOT be 239,187,191 (UTF-8 BOM)
$bytes = [IO.File]::ReadAllBytes($f)
Write-Host "BOM check: $($bytes[0]),$($bytes[1]),$($bytes[2])  (must NOT be 239,187,191)"
# First content line must show ⚡ not âš¡
$preview = [Text.Encoding]::UTF8.GetString($bytes[0..200])
Write-Host $preview
```

---

### Git Workflow

```bash
git add dictionary/
git commit -m "feat: add <CODE>-<NNN>-<CODE>-<NNN> <Category> - batch <N>"
# Do NOT git push
```

Upgrade commits: `"upgrade: →LATEST_VERSION_LABEL <CODE>-<NNN>-<CODE>-<NNN> - batch N"`
