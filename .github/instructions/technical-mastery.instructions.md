---
applyTo: "technical-mastery/**"
description: "Rules for generating and editing Technical Mastery v6.0 entries - 24 sections, YAML format, Category Code Registry"
---

# Technical Mastery - Auto-Loaded Instructions

> These instructions auto-attach when editing files under `technical-mastery/`.
> Full generation spec: `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md`

## Workspace Structure

```
technical-mastery/
  _config/
    ENTRY_GENERATOR_PROMPT.md               # Master generation spec v6.0
    MASTERY_OS_PROMPT.md       # Category keyword generator v6.0
    CATEGORY_GENERATOR_PROMPT.md      # Single-category generator v2.0
    TECHNICAL_MASTERY_LIST.md           # READ-ONLY reference. Permitted uses: (1) check existing IDs for conflicts; (2) verify topic coverage. Prohibited: generating or deriving any keywords from it.
    GENERATE_QUEUE.md                 # Generation queue guide
  index.md                            # Site root nav node
  tier-1-foundations/
  tier-2-networking-security/
  tier-3-java/
  tier-4-data/
  tier-5-distributed-architecture/
  tier-6-infrastructure-devops/
  tier-7-frontend/
  tier-8-artificial-intelligence/
  tier-9-professional-domain/
```

## Prompts (in .github/prompts/)

| Prompt                    | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| `@technical-mastery-generate-entries`  | Generate v6.0 entries from stubs          |
| `@technical-mastery-generate-keywords` | Generate keyword lists, sync index, stubs |
| `@technical-mastery-upgrade-batch`     | Upgrade entries to v6.0 standard          |

## Version Registry

| Constant               | Value  | Meaning                                        |
| ---------------------- | ------ | ---------------------------------------------- |
| `LATEST_VERSION`       | `6`    | Integer for `version:` in all complete entries |
| `LATEST_VERSION_LABEL` | `v6.0` | Human-readable label for headers/commits       |
| `STUB_VERSION`         | `0`    | Integer for placeholder stubs                  |

## Rules Summary (apply in order)

**0. KEYWORD GENERATION (NON-NEGOTIABLE):** Any keyword list - for any
topic, technology, language, skill, feature, description, JD text, or
anything else - MUST be generated using `MASTERY_OS_PROMPT.md`
v6.0. All 33 rules, all 30 quality checks. No exceptions.
`TECHNICAL_MASTERY_LIST.md` has two permitted uses ONLY:
(1) verify a keyword ID does not already exist;
(2) confirm which topics a category already covers.
All other use is prohibited - especially generating, deriving, or
copying keywords from it. ALL keyword generation goes through
`MASTERY_OS_PROMPT.md` only. `TECHNICAL_MASTERY_LIST.md` is updated
ONLY AFTER the keyword list is generated.

**1. Content:** All 24 required sections in exact sequence (5.1-5.24). BAD-before-GOOD code. Min 4 misconception rows, min 3 failure modes.

**2. Conditional sections** - use this decision table:

| Section               | Include when...                                     | Omit when...                              |
| :-------------------- | :-------------------------------------------------- | :---------------------------------------- |
| 5.13 Code Example     | Direct programmatic expression (class, API, config) | Purely theoretical concept                |
| 5.14 Comparison Table | 2+ named alternatives/variants exist                | Concept is unique, no alternative         |
| 5.15 Flow / Lifecycle | Distinct ordered multi-phase lifecycle (3+ phases)  | Data structure, algorithm, single pattern |

If the condition is ambiguous, include the section.

**3. Formatting:** `---` before every `###`. ASCII diagrams: each line must not exceed 59 characters in width. Diagrams: DUAL format (ASCII first, then Mermaid below). Types: `flowchart`, `sequenceDiagram`, `stateDiagram-v2`, `classDiagram`, `erDiagram`, `mindmap`. Code lines max 70 chars. No H2 headers. No `# H1` in body - Just the Docs renders H1 from YAML `title`. Bold-label lines (`**LABEL:** value`) must each be separated by a blank line.

**4. YAML:** All required frontmatter fields. Double-quote titles with `: `. No em dashes anywhere. If a required field is missing or invalid, halt and specify which field needs to be supplied before proceeding.

**5. Versions:** Complete entries = `version: 4`, stubs = `version: 0`. Scale: 0|1|2|3|4.

## Entry Structure - 24 Sections

| #    | Section Header                                      | Status      |
| ---- | --------------------------------------------------- | ----------- |
| 5.1  | YAML `title` generates H1 (no `#` in body)          | Required    |
| 5.2  | TL;DR (max 25 words)                                | Required    |
| 5.3  | Metadata table                                      | Required    |
| 5.4  | The Problem This Solves (+EVOLUTION)                | Required    |
| 5.5  | Textbook Definition                                 | Required    |
| 5.6  | Understand It in 30 Seconds                         | Required    |
| 5.7  | First Principles (+Essential/Accidental)            | Required    |
| 5.8  | Thought Experiment                                  | Required    |
| 5.9  | Mental Model / Analogy                              | Required    |
| 5.10 | Gradual Depth - Five Levels (+Expert Cues L5)       | Required    |
| 5.11 | How It Works (+Concurrency if applicable)           | Required    |
| 5.12 | Complete Picture - End-to-End Flow                  | Required    |
| 5.13 | Code Example (BAD then GOOD + testing)              | Conditional |
| 5.14 | Comparison Table                                    | Conditional |
| 5.15 | Flow / Lifecycle                                    | Conditional |
| 5.16 | Common Misconceptions (min 4 rows)                  | Required    |
| 5.17 | Failure Modes & Diagnosis (min 3 + Security)        | Required    |
| 5.18 | Related Keywords (3 categories)                     | Required    |
| 5.19 | Quick Reference Card (9-row + 3 things + interview) | Required    |
| 5.20 | Transferable Wisdom (+industry apps)                | Required    |
| 5.21 | The Surprising Truth (1 fact)                       | Required    |
| 5.22 | Mastery Checklist (5 indicators)                    | Required    |
| 5.23 | Think About This (3 Qs + 1 TYPE G)                  | Required    |
| 5.24 | Interview Deep-Dive (3-7 Qs by difficulty)          | Required    |

## ID System

Format: `[CODE]-[NNN]` (e.g. `JVM-036`). Permanent, collision-proof. Next ID = highest in folder + 1.

## YAML Frontmatter (Required Fields)

```yaml
---
id: CODE-NNN
title: Keyword Name
category: Full Category Name
tier: tier-N-name
folder: CODE-folder-name
difficulty: ★☆☆ | ★★☆ | ★★★
depends_on: CODE-NNN, CODE-NNN
used_by: CODE-NNN, CODE-NNN
related: CODE-NNN, CODE-NNN
tags: [yaml array, 3-6 tags]
status: draft | in-progress | complete
version: 0 | 1 | 2 | 3 | 4
layout: default
parent: "Full Category Name"
grand_parent: "Technical Mastery"
nav_order: NNN
permalink: /technical-mastery/category-slug/keyword-slug/
---
```

## File Naming

`[CODE]-[NNN] - Keyword Name.md` (SPACE-HYPHEN-SPACE separator, NEVER em dash)

## Category Code Registry

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

## Quality Constitution (Non-Negotiable)

**Priority order when constraints conflict:** YAML validity -> Section completeness (5.1-5.24) -> Formatting -> Content depth.

Full spec: `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md` Section 7.
Every entry MUST pass ALL eight quality tests before output.

### Eight Quality Tests

| #   | Test               | If FAIL                                                 |
| --- | ------------------ | ------------------------------------------------------- |
| 1   | Search Again?      | Reader still needs to look elsewhere = incomplete       |
| 2   | Feynman            | Smart beginner confused = rewrite                       |
| 3   | Senior Engineer    | Senior learns nothing new = too shallow                 |
| 4   | Staff Engineer     | Staff wouldn't respect this = lacks depth               |
| 5   | Production Reality | Can't diagnose real issue = add diagnostics             |
| 6   | Retention          | Won't remember next month = add memory hooks            |
| 7   | Decision           | Can't decide when to use/avoid = add decision framework |
| 8   | Scale              | No 10x/100x/1000x coverage = add scale analysis         |

### Code Example Requirements

Every concept with code must include at minimum:
- **MANDATORY:** Wrong vs Right Example (BAD before GOOD, always)
- **MANDATORY:** Failure Example (what breaks, symptoms, fix)
- **Plus 1-2 more** based on complexity:

| Category                  | Use when...                              |
| ------------------------- | ---------------------------------------- |
| Recognition Example       | Pattern appears in real codebases        |
| Production Example        | Real-world usage, not toy                |
| Debugging Example         | Diagnostic commands or log analysis      |
| Scale Example             | Behavior changes under load              |
| Trade-off Example         | Gain vs sacrifice decision               |
| Internal Mechanism Example| How it works underneath                  |
| System Interaction Example| Cross-component behavior                 |
| Testing/Verification      | Prove correctness                        |

Goal: reader understands why, when, failure, scale, debugging, and trade-offs.

### 10-Point Writing Standard

Every explanation must cover: (1) Intuition, (2) Mechanism, (3) Trade-off, (4) Failure, (5) Diagnosis, (6) Scale, (7) Decision, (8) Memory, (9) Transfer, (10) Reality

### Forbidden Patterns

- Generic textbook definitions only
- Syntax-only or toy code examples
- Vague advice ("it depends") without specifics
- Fabricated benchmarks or performance numbers
- Surface-level explanations that skip WHY
- "Best practice" claims without reasoning
- Walls of prose without structure
- Repetition across sections

### Final Gate

"Would an experienced engineer say 'Damn - this is genuinely excellent'?" If uncertain: rewrite.

## Encoding Safety

- Always use `pwsh` (PowerShell 7+), NEVER `powershell.exe`
- UTF-8 without BOM: `[System.Text.UTF8Encoding]::new($false)`
- Python: `$env:USERPROFILE\.local\bin\python3.14.exe`

## Git Workflow

```bash
git add technical-mastery/
git commit -m "feat: add <CODE>-<START>-<CODE>-<END> <Category> - batch <N>"
# Do NOT git push
# Do NOT commit single files
```

**Batch Commit Rules (Non-Negotiable):**

- Commit every **10 created files** (never single files)
- Only commit files that were **created** (not just modified/upgraded)
- If fewer than 10 remain at the end, commit all remaining at once
- Include ID range in commit message (e.g. `DST-078-DST-087`)
- Do NOT `git push`

> For the complete 671-line spec with full section rules, teaching philosophy, key section rules, and version detection, see `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md`.
