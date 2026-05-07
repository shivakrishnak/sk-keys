$file = "c:\ASK\MyWorkspace\sk-keys\GENERATOR_PROMPT.md"
$enc  = [System.Text.UTF8Encoding]::new($false)
$c    = [System.IO.File]::ReadAllText($file, $enc)
$nl   = "`r`n"   # CRLF — preserve Windows line endings

Write-Host "Loaded $($c.Length) chars"

# ══════════════════════════════════════════════════════════════
# SECTION 2: replace FILE FORMAT → ID SYSTEM
# ══════════════════════════════════════════════════════════════

$sec2_old = @'
═══════════════════════════════════════════════════════════════════════════
SECTION 2: FILE FORMAT — OBSIDIAN MARKDOWN
═══════════════════════════════════════════════════════════════════════════

Each keyword is a SINGLE MARKDOWN FILE.
Every entry must be 100% self-contained — no "see entry X for details."

File naming convention:
  NNN — Keyword Name.md
  Examples:
    261 — JVM.md
    036 — JIT Compiler.md
    1293 — Event Loop.md

The file begins with YAML frontmatter, then content.
No other file structure is permitted.
'@

$sec2_new = @'
═══════════════════════════════════════════════════════════════════════════
SECTION 2: ID SYSTEM, FILE FORMAT & FOLDER STRUCTURE
═══════════════════════════════════════════════════════════════════════════

Each keyword is a SINGLE MARKDOWN FILE.
Every entry must be 100% self-contained — no "see entry X for details."

─────────────────────────────────────────────────────────────────────────
ID FORMAT
─────────────────────────────────────────────────────────────────────────

  [CATEGORY_CODE]-[SEQUENCE]

  CATEGORY_CODE:
    - 3 uppercase letters, uniquely identifies the category
    - Never changes once assigned
    - See Category Code Registry below

  SEQUENCE:
    - 3-digit zero-padded integer (e.g. 001, 036, 074)
    - Unique WITHIN a category only
    - Starts at 001 for every category
    - Extends to 4 digits (0001) if category exceeds 999 entries

  EXAMPLES:
    JVM-001   ← Java & JVM Internals, entry 1
    JVM-036   ← Java & JVM Internals, entry 36
    SEC-001   ← Security, entry 1
    DSA-074   ← Data Structures & Algorithms, entry 74

  CORE RULES:
    - IDs are PERMANENT — once assigned, never change
    - IDs are collision-proof — JVM-001 ≠ SEC-001
    - NEXT ID = open folder → find highest sequence → add 1
    - NEW CATEGORY = new 3-letter code, start at 001
    - Prefix uniqueness enforced ONCE at category creation

─────────────────────────────────────────────────────────────────────────
FILE NAMING CONVENTION
─────────────────────────────────────────────────────────────────────────

  [ID] — [Keyword Name].md

  Separator: space + em dash + space ( — )
  Extension: .md always

  EXAMPLES:
    JVM-001 — JVM.md
    JVM-036 — JIT Compiler.md
    SEC-023 — CSRF.md
    DSA-048 — Dynamic Programming.md
    LLM-035 — LLM-as-Judge Pattern.md

  WIKILINK FORMAT (in entry body):
    [[JVM-036 — JIT Compiler]]      ← always full filename
    [[SEC-023 — CSRF]]
    Always include full ID + keyword name — never ID alone.

─────────────────────────────────────────────────────────────────────────
FOLDER STRUCTURE
─────────────────────────────────────────────────────────────────────────

  /dictionary/
  ├── /tier-1-foundations/
  │     ├── /CSF-cs-fundamentals/
  │     ├── /DSA-data-structures/
  │     ├── /OSY-operating-systems/
  │     └── /LNX-linux/
  ├── /tier-2-networking-security/
  │     ├── /NET-networking/
  │     ├── /API-http-apis/
  │     └── /SEC-security/
  ├── /tier-3-java/
  │     ├── /JVM-java-jvm-internals/
  │     ├── /JLG-java-language/
  │     ├── /JCC-java-concurrency/
  │     └── /SPR-spring-core/
  ├── /tier-4-data/
  │     ├── /DBF-database-fundamentals/
  │     ├── /NDB-nosql-distributed/
  │     ├── /CCH-caching/
  │     ├── /DAT-data-fundamentals/
  │     └── /BIG-bigdata-streaming/
  ├── /tier-5-distributed-architecture/
  │     ├── /DST-distributed-systems/
  │     ├── /MSV-microservices/
  │     ├── /SYD-system-design/
  │     ├── /SAP-software-architecture/
  │     └── /DPT-design-patterns/
  ├── /tier-6-infrastructure-devops/
  │     ├── /CTR-containers/
  │     ├── /K8S-kubernetes/
  │     ├── /AWS-cloud-aws/
  │     ├── /AZR-cloud-azure/
  │     ├── /CCD-cicd/
  │     ├── /GIT-git-branching/
  │     ├── /MVN-maven-build/
  │     ├── /CDQ-code-quality/
  │     ├── /TST-testing/
  │     ├── /OBS-observability-sre/
  │     └── /IAC-infrastructure-code/
  ├── /tier-7-frontend/
  │     ├── /HTM-html/
  │     ├── /CSS-css/
  │     ├── /JSC-javascript/
  │     ├── /TSC-typescript/
  │     ├── /RCT-react/
  │     ├── /ANG-angular/
  │     ├── /NDJ-nodejs/
  │     ├── /NPM-npm-packages/
  │     └── /WBP-webpack-build/
  ├── /tier-8-artificial-intelligence/
  │     ├── /AIF-ai-foundations/
  │     ├── /LLM-llms-prompt-eng/
  │     ├── /RAG-rag-agents-llmops/
  │     └── /AIP-ai-product/
  └── /tier-9-professional-domain/
        ├── /ASY-async-background/
        ├── /DGN-document-generation/
        ├── /FIN-financial-domain/
        ├── /PLT-platform-swe/
        └── /BHV-behavioral-leadership/

  Folder naming rules:
    Tier folders:     tier-[N]-[descriptive-name]
    Category folders: [CODE]-[descriptive-name]
    Folder names NEVER change after creation.
    The CODE in the folder = the ID prefix — they must match.

─────────────────────────────────────────────────────────────────────────
CATEGORY CODE REGISTRY
─────────────────────────────────────────────────────────────────────────

  CODE | Category Name                     | Tier
  ─────┼───────────────────────────────────┼──────────────────────────────
  CSF  | CS Fundamentals — Paradigms       | tier-1-foundations
  DSA  | Data Structures & Algorithms      | tier-1-foundations
  OSY  | Operating Systems                 | tier-1-foundations
  LNX  | Linux                             | tier-1-foundations
  NET  | Networking                        | tier-2-networking-security
  API  | HTTP & APIs                       | tier-2-networking-security
  SEC  | Security                          | tier-2-networking-security
  JVM  | Java & JVM Internals              | tier-3-java
  JLG  | Java Language                     | tier-3-java
  JCC  | Java Concurrency                  | tier-3-java
  SPR  | Spring Core                       | tier-3-java
  DBF  | Database Fundamentals             | tier-4-data
  NDB  | NoSQL & Distributed Databases     | tier-4-data
  CCH  | Caching                           | tier-4-data
  DAT  | Data Fundamentals                 | tier-4-data
  BIG  | Big Data & Streaming              | tier-4-data
  DST  | Distributed Systems               | tier-5-distributed-architecture
  MSV  | Microservices                     | tier-5-distributed-architecture
  SYD  | System Design                     | tier-5-distributed-architecture
  SAP  | Software Architecture Patterns    | tier-5-distributed-architecture
  DPT  | Design Patterns                   | tier-5-distributed-architecture
  CTR  | Containers                        | tier-6-infrastructure-devops
  K8S  | Kubernetes                        | tier-6-infrastructure-devops
  AWS  | Cloud — AWS                       | tier-6-infrastructure-devops
  AZR  | Cloud — Azure                     | tier-6-infrastructure-devops
  CCD  | CI/CD                             | tier-6-infrastructure-devops
  GIT  | Git & Branching Strategy          | tier-6-infrastructure-devops
  MVN  | Maven & Build Tools               | tier-6-infrastructure-devops
  CDQ  | Code Quality                      | tier-6-infrastructure-devops
  TST  | Testing                           | tier-6-infrastructure-devops
  OBS  | Observability & SRE               | tier-6-infrastructure-devops
  IAC  | Infrastructure as Code            | tier-6-infrastructure-devops
  HTM  | HTML                              | tier-7-frontend
  CSS  | CSS                               | tier-7-frontend
  JSC  | JavaScript                        | tier-7-frontend
  TSC  | TypeScript                        | tier-7-frontend
  RCT  | React                             | tier-7-frontend
  ANG  | Angular                           | tier-7-frontend
  NDJ  | Node.js                           | tier-7-frontend
  NPM  | npm & Package Management          | tier-7-frontend
  WBP  | Webpack & Build Tools             | tier-7-frontend
  AIF  | AI Foundations                    | tier-8-artificial-intelligence
  LLM  | LLMs & Prompt Engineering         | tier-8-artificial-intelligence
  RAG  | RAG & Agents & LLMOps             | tier-8-artificial-intelligence
  AIP  | AI Product Engineering            | tier-8-artificial-intelligence
  ASY  | Async & Background Processing     | tier-9-professional-domain
  DGN  | Document Generation               | tier-9-professional-domain
  FIN  | Financial Services Domain         | tier-9-professional-domain
  PLT  | Platform & Modern SWE             | tier-9-professional-domain
  BHV  | Behavioral & Leadership           | tier-9-professional-domain

  TOTAL: 50 categories across 9 tiers

  TO ADD A NEW CATEGORY:
    1. Choose a unique 3-letter code not in this list
    2. Add to the correct tier section in this registry
    3. Create the folder: /tier-N-name/CODE-descriptive-name/
    4. First entry = [CODE]-001
'@

# Normalize line endings in old string to match file (CRLF)
$sec2_old_crlf = $sec2_old -replace "`r`n", "`n" -replace "`n", "`r`n"
$sec2_new_crlf = $sec2_new -replace "`r`n", "`n" -replace "`n", "`r`n"

if ($c.Contains($sec2_old_crlf)) {
    $c = $c.Replace($sec2_old_crlf, $sec2_new_crlf)
    Write-Host "✅ Section 2 replaced"
} elseif ($c.Contains($sec2_old)) {
    $c = $c.Replace($sec2_old, $sec2_new_crlf)
    Write-Host "✅ Section 2 replaced (LF match)"
} else {
    Write-Host "❌ Section 2 NOT matched — checking fragment..."
    Write-Host "Fragment found: $($c.Contains('SECTION 2: FILE FORMAT'))"
}

# ══════════════════════════════════════════════════════════════
# SECTION 3: replace YAML FRONTMATTER spec
# ══════════════════════════════════════════════════════════════

$sec3_old = @'
═══════════════════════════════════════════════════════════════════════════
SECTION 3: YAML FRONTMATTER — EXACT FORMAT
═══════════════════════════════════════════════════════════════════════════

Every file MUST begin with this EXACT structure.
No extra fields. No missing fields. No deviations.

---
layout: default
title: "Keyword Name"
parent: "Category Name"
nav_order: NNNN
permalink: /category-slug/keyword-slug/
number: "NNNN"
category: Category Name
difficulty: ★☆☆
depends_on: Keyword1, Keyword2, Keyword3
used_by: Keyword1, Keyword2, Keyword3
related: Keyword1, Keyword2, Keyword3
tags:
  - tag1
  - tag2
  - tag3
---

FIELD RULES:

layout:
  - Always: default
  - Fixed value — never change

title:
  - The keyword name in double quotes
  - Must match the H1 title line exactly
  - Example: "Event Loop", "Vertical Scaling", "JVM"

parent:
  - The exact category title that matches the category folder's index.md
  - Must come from the category → parent mapping table (see batch workflow)
  - Example: "System Design", "Java & JVM Internals", "Testing"

nav_order:
  - The global keyword number as a plain integer (no quotes, no padding)
  - Used by Just the Docs for sidebar ordering
  - Example: 681, 261, 1293

permalink:
  - Derived from: /<category-slug>/<keyword-slug>/
  - category-slug: lowercase, hyphens, no special chars
  - keyword-slug: lowercase version of the keyword name
    (spaces → hyphens, remove parentheses, ampersands → and)
  - Example: /system-design/vertical-scaling/
             /java/jvm/
             /testing/unit-test/
  - Use the category slug from the mapping table in the batch workflow

number:
  - Four-digit zero-padded integer, in double quotes
  - Example: "0001", "0261", "1293"

category:
  - Exact category name from master list (no quotes)
  - Valid values:
    CS Fundamentals — Paradigms |
    Data Structures & Algorithms |
    Operating Systems |
    Linux |
    Networking |
    HTTP & APIs |
    Java & JVM Internals |
    Java Language |
    Java Concurrency |
    Spring Core |
    Database Fundamentals |
    NoSQL & Distributed Databases |
    Caching |
    Data Fundamentals |
    Big Data & Streaming |
    Distributed Systems |
    Microservices |
    System Design |
    Software Architecture Patterns |
    Design Patterns |
    Containers |
    Kubernetes |
    Cloud — AWS |
    Cloud — Azure |
    CI/CD |
    Git & Branching Strategy |
    Maven & Build Tools |
    Code Quality |
    Testing |
    Observability & SRE |
    HTML |
    CSS |
    JavaScript |
    TypeScript |
    React |
    Node.js |
    npm & Package Management |
    Webpack & Build Tools |
    AI Foundations |
    LLMs & Prompt Engineering |
    RAG & Agents & LLMOps |
    Platform & Modern SWE |
    Behavioral & Leadership

difficulty:
  - EXACTLY one of three values:
    ★☆☆  →  Foundational
    ★★☆  →  Intermediate
    ★★★  →  Deep-dive

depends_on:
  - Concepts reader MUST know BEFORE this entry
  - Comma-separated plain text
  - NO brackets, NO wiki links
  - Maximum 5

used_by:
  - Concepts that BUILD ON this concept
  - Comma-separated plain text
  - NO brackets, NO wiki links
  - Maximum 5

related:
  - Sibling concepts at same level (alternatives, comparisons)
  - Captures lateral connections
  - Comma-separated plain text
  - NO brackets, NO wiki links
  - Maximum 5

tags:
  - Each tag without # prefix
  - Listed as YAML array items (one per line, using "-")
  - Choose from approved tag taxonomy (see Section 4)
  - 3–6 tags per entry
  - Example:
    - java
    - jvm
    - memory
    - internals
    - deep-dive
'@

$sec3_new = @'
═══════════════════════════════════════════════════════════════════════════
SECTION 3: YAML FRONTMATTER — EXACT FORMAT
═══════════════════════════════════════════════════════════════════════════

Every entry file MUST begin with this EXACT frontmatter.
No extra fields. No missing fields. No deviations.

---
id: [CODE]-[NNN]
title: [Exact Keyword Name]
category: [Full Category Name]
tier: [tier-N-name]
folder: [CODE-folder-name]
difficulty: [★☆☆ | ★★☆ | ★★★]
depends_on: [CODE]-[NNN], [CODE]-[NNN]
used_by: [CODE]-[NNN], [CODE]-[NNN]
related: [CODE]-[NNN], [CODE]-[NNN]
tags: #tag1, #tag2, #tag3
status: [draft | in-progress | complete]
version: 1
---

FIELD RULES:

id:
  - The permanent identifier — format: [CODE]-[NNN]
  - CODE: 3-letter category code from Section 2 registry
  - NNN: zero-padded sequence within category (001, 036, 074)
  - Never changes after assignment
  - Example: JVM-036, SEC-023, DSA-048

title:
  - Exact keyword name from master keyword list
  - Matches the filename keyword portion exactly
  - NO quotes required
  - Example: JIT Compiler, CSRF, Dynamic Programming

category:
  - Full human-readable category name
  - Must match exactly the name in Section 2 registry
  - Example: Java & JVM Internals, Security, Data Structures & Algorithms

tier:
  - The tier folder name this entry lives in
  - From Section 2 registry column "Tier"
  - Example: tier-3-java, tier-2-networking-security
  - Used for filtering entries by tier

folder:
  - The category folder name (CODE + descriptive suffix)
  - From Section 2 registry column "Folder"
  - Example: JVM-java-jvm-internals, SEC-security
  - Used for filtering entries by category

difficulty:
  - EXACTLY one of three values:
    ★☆☆  →  Foundational
    ★★☆  →  Intermediate
    ★★★  →  Deep-dive

depends_on:
  - IDs of entries that MUST be understood first
  - Comma-separated full IDs: JVM-001, DSA-048
  - NO brackets, NO wiki syntax, NO keyword names
  - Cross-category references are explicit: JVM-001, SEC-023
  - Maximum 5 entries

used_by:
  - IDs of entries that BUILD ON this entry
  - Same format as depends_on
  - Maximum 5 entries

related:
  - IDs of sibling / alternative / comparison entries
  - Same format as depends_on
  - Maximum 5 entries

tags:
  - # prefixed, comma-separated on ONE line
  - 3–6 tags per entry
  - From approved taxonomy only (see Section 4)
  - Example: #java, #jvm, #performance, #deep-dive

status:
  - draft        → keyword exists, entry not yet written
  - in-progress  → entry partially written
  - complete     → entry fully written and reviewed

version:
  - Integer, starts at 1
  - Increment when entry is substantially revised

─────────────────────────────────────────────────────────────────────────
COMPLETE EXAMPLE — CORRECT FRONTMATTER:
─────────────────────────────────────────────────────────────────────────

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
tags: #java, #jvm, #performance, #deep-dive
status: complete
version: 1
---
'@

$sec3_old_crlf = $sec3_old -replace "`r`n", "`n" -replace "`n", "`r`n"
$sec3_new_crlf = $sec3_new -replace "`r`n", "`n" -replace "`n", "`r`n"

if ($c.Contains($sec3_old_crlf)) {
    $c = $c.Replace($sec3_old_crlf, $sec3_new_crlf)
    Write-Host "✅ Section 3 replaced"
} elseif ($c.Contains($sec3_old)) {
    $c = $c.Replace($sec3_old, $sec3_new_crlf)
    Write-Host "✅ Section 3 replaced (LF match)"
} else {
    Write-Host "❌ Section 3 NOT matched"
    Write-Host "Fragment found: $($c.Contains('SECTION 3: YAML FRONTMATTER'))"
}

# ══════════════════════════════════════════════════════════════
# SECTION 4: update Tag Taxonomy (add new tags)
# ══════════════════════════════════════════════════════════════

$sec4_old_platform = "Platform / Runtime:$nl  #java #jvm #spring #springboot #javascript #typescript$nl  #react #nodejs #css #html #webpack #npm #kotlin #graalvm$nl  #docker #kubernetes #linux #aws #azure #python #rust"

$sec4_new_platform = "Platform / Runtime:$nl  #java #jvm #spring #springboot #javascript #typescript$nl  #react #angular #nodejs #css #html #webpack #npm #kotlin$nl  #graalvm #docker #kubernetes #linux #aws #azure #gcp$nl  #python #rust"

$sec4_old_domain = "Domain:$nl  #internals #concurrency #memory #gc #networking #distributed$nl  #database #messaging #security #os #cloud #containers #devops$nl  #performance #architecture #reliability #observability$nl  #frontend #rendering #browser #bundling #testing #cicd$nl  #git #build #dataengineering #bigdata #streaming #caching$nl  #ai #llm #agents #rag #mlops #microservices #api"

$sec4_new_domain = "Domain:$nl  #internals #concurrency #memory #gc #networking #distributed$nl  #database #messaging #security #os #cloud #containers #devops$nl  #performance #architecture #reliability #observability$nl  #frontend #rendering #browser #bundling #testing #cicd$nl  #git #build #dataengineering #bigdata #streaming #caching$nl  #ai #llm #agents #rag #mlops #microservices #api$nl  #iac #terraform #async #finance #documents"

if ($c.Contains($sec4_old_platform)) {
    $c = $c.Replace($sec4_old_platform, $sec4_new_platform)
    Write-Host "✅ Section 4 platform tags updated"
} else {
    Write-Host "❌ Section 4 platform tags NOT matched"
}

if ($c.Contains($sec4_old_domain)) {
    $c = $c.Replace($sec4_old_domain, $sec4_new_domain)
    Write-Host "✅ Section 4 domain tags updated"
} else {
    Write-Host "❌ Section 4 domain tags NOT matched"
}

# ══════════════════════════════════════════════════════════════
# SECTION 5.1: update title format
# ══════════════════════════════════════════════════════════════

$s51_old = "─────────────────────────────────────────────────────────────────────────$nl5.1  TITLE LINE  [REQUIRED]$nl─────────────────────────────────────────────────────────────────────────$nl$nl Format:$nl  # NNN — KEYWORD NAME"

$s51_new = "─────────────────────────────────────────────────────────────────────────$nl5.1  TITLE LINE  [REQUIRED]$nl─────────────────────────────────────────────────────────────────────────$nl$nl Format:$nl  # [CODE]-[NNN] — KEYWORD NAME"

if ($c.Contains($s51_old)) {
    $c = $c.Replace($s51_old, $s51_new)
    Write-Host "✅ Section 5.1 title format updated"
} else {
    Write-Host "❌ Section 5.1 NOT matched"
}

# ══════════════════════════════════════════════════════════════
# SECTION 8: update skeleton frontmatter + title
# ══════════════════════════════════════════════════════════════

$sec8_fm_old = @'
---
layout: default
title: "Keyword Name"
parent: "Category Name"
nav_order: NNNN
permalink: /category-slug/keyword-slug/
number: "NNNN"
category: Category Name
difficulty: [★☆☆ | ★★☆ | ★★★]
depends_on: Keyword1, Keyword2
used_by: Keyword1, Keyword2
related: Keyword1, Keyword2
tags:
  - tag1
  - tag2
  - tag3
---

# NNNN — KEYWORD NAME
'@

$sec8_fm_new = @'
---
id: [CODE]-[NNN]
title: [Keyword Name]
category: [Full Category Name]
tier: [tier-N-name]
folder: [CODE-folder-name]
difficulty: [★☆☆ | ★★☆ | ★★★]
depends_on: [CODE]-[NNN], [CODE]-[NNN]
used_by: [CODE]-[NNN], [CODE]-[NNN]
related: [CODE]-[NNN], [CODE]-[NNN]
tags: #tag1, #tag2, #tag3
status: draft
version: 1
---

# [CODE]-[NNN] — KEYWORD NAME
'@

$sec8_fm_old_crlf = $sec8_fm_old -replace "`r`n", "`n" -replace "`n", "`r`n"
$sec8_fm_new_crlf = $sec8_fm_new -replace "`r`n", "`n" -replace "`n", "`r`n"

if ($c.Contains($sec8_fm_old_crlf)) {
    $c = $c.Replace($sec8_fm_old_crlf, $sec8_fm_new_crlf)
    Write-Host "✅ Section 8 skeleton updated"
} elseif ($c.Contains($sec8_fm_old)) {
    $c = $c.Replace($sec8_fm_old, $sec8_fm_new_crlf)
    Write-Host "✅ Section 8 skeleton updated (LF match)"
} else {
    Write-Host "❌ Section 8 NOT matched"
    Write-Host "Fragment check (layout: default): $($c.Contains('layout: default'))"
}

# ══════════════════════════════════════════════════════════════
# SECTION 9: update invocation commands
# ══════════════════════════════════════════════════════════════

$sec9_old = @'
SINGLE ENTRY:

  Generate dictionary entry for keyword: [KEYWORD NAME]
  Number: [NNNN]
  Category: [CATEGORY NAME]
  Difficulty: [★☆☆ | ★★☆ | ★★★]

  Follow the Technical Dictionary Generator prompt v2.1 exactly.
  Use the complete skeleton from Section 8.
  Do not skip any required section.
  Do not add sections not in the spec.
  Apply all 12 teaching principles from Section 1.

BATCH OF 5:

  Generate dictionary entries for keywords NNNN–NNNN:
  - [KEYWORD 1] (NNNN) — [difficulty]
  - [KEYWORD 2] (NNNN) — [difficulty]
  - [KEYWORD 3] (NNNN) — [difficulty]
  - [KEYWORD 4] (NNNN) — [difficulty]
  - [KEYWORD 5] (NNNN) — [difficulty]

  Follow Technical Dictionary Generator v2.1 exactly.
  Each entry is a separate markdown file.
  Sequential numbering.
  Each entry fully self-contained.

CONTINUE FROM LAST:

  Continue dictionary generation from entry NNNN.
  Next: [KEYWORD 1] through [KEYWORD 5].
  Follow Technical Dictionary Generator v2.1 exactly.
'@

$sec9_new = @'
SINGLE ENTRY:

  Generate dictionary entry:
    ID:         [CODE]-[NNN]
    Keyword:    [Exact Keyword Name]
    Category:   [Full Category Name]
    Tier:       [tier-N-name]
    Folder:     [CODE-folder-name]
    Difficulty: [★☆☆ | ★★☆ | ★★★]

  Follow Master Prompt v2.1 (content rules) exactly.
  Follow ID System v3.0 (ID/file/folder rules) exactly.
  Use the complete skeleton from Section 8.
  Do not skip any required section.
  Do not add sections not in the spec.
  Apply all 12 teaching principles from Section 1.

BATCH OF 5:

  Generate dictionary entries [CODE]-[NNN] through [CODE]-[NNN]:

    [CODE]-[NNN] | [Keyword 1] | [★difficulty]
    [CODE]-[NNN] | [Keyword 2] | [★difficulty]
    [CODE]-[NNN] | [Keyword 3] | [★difficulty]
    [CODE]-[NNN] | [Keyword 4] | [★difficulty]
    [CODE]-[NNN] | [Keyword 5] | [★difficulty]

  Category:   [Full Category Name]
  Tier:       [tier-N-name]
  Folder:     [CODE-folder-name]

  Follow Master Prompt v2.1 (content) exactly.
  Follow ID System v3.0 (IDs/files/folders) exactly.
  Each entry is a separate markdown file.
  Sequential IDs — no gaps.
  Each entry fully self-contained.

CONTINUE FROM LAST:

  Continue dictionary generation for category: [CODE]
  Last generated: [CODE]-[NNN]
  Next batch: [CODE]-[NNN] through [CODE]-[NNN]

  Confirm next ID = last + 1.
  Follow Master Prompt v2.1 and ID System v3.0 exactly.

CROSS-CATEGORY BATCH:

  Generate the following dictionary entries:

    [CODE]-[NNN] | [Keyword 1] | [Category 1] | [★difficulty]
    [CODE]-[NNN] | [Keyword 2] | [Category 2] | [★difficulty]
    [CODE]-[NNN] | [Keyword 3] | [Category 3] | [★difficulty]

  Each entry goes in its own category folder.
  Cross-category depends_on uses full IDs: JVM-001, SEC-023.
  Follow Master Prompt v2.1 and ID System v3.0 exactly.
'@

$sec9_old_crlf = $sec9_old -replace "`r`n", "`n" -replace "`n", "`r`n"
$sec9_new_crlf = $sec9_new -replace "`r`n", "`n" -replace "`n", "`r`n"

if ($c.Contains($sec9_old_crlf)) {
    $c = $c.Replace($sec9_old_crlf, $sec9_new_crlf)
    Write-Host "✅ Section 9 invocation updated"
} elseif ($c.Contains($sec9_old)) {
    $c = $c.Replace($sec9_old, $sec9_new_crlf)
    Write-Host "✅ Section 9 invocation updated (LF match)"
} else {
    Write-Host "❌ Section 9 NOT matched"
    Write-Host "Fragment check (SINGLE ENTRY): $($c.Contains('SINGLE ENTRY:'))"
}

# ══════════════════════════════════════════════════════════════
# SECTION 10: update FRONTMATTER checklist
# ══════════════════════════════════════════════════════════════

$sec10_fm_old = "FRONTMATTER:$nl  ☐ layout: always `"default`"$nl  ☐ title: keyword name in double quotes, matches H1 title$nl  ☐ parent: exact category title from mapping table$nl  ☐ nav_order: plain integer matching the keyword number$nl  ☐ permalink: /category-slug/keyword-slug/ (lowercase, hyphenated)$nl  ☐ number: 4-digit padded in double quotes, matches filename$nl  ☐ category: from approved list (Section 3), no quotes$nl  ☐ difficulty: exactly one of three star values$nl  ☐ depends_on: plain text, no brackets, max 5$nl  ☐ used_by: plain text, no brackets, max 5$nl  ☐ related: plain text, no brackets, max 5$nl  ☐ tags: YAML array items, no # prefix, from taxonomy (Section 4)"

$sec10_fm_new = "FRONTMATTER:$nl  ☐ All 12 fields present: id, title, category, tier, folder,$nl    difficulty, depends_on, used_by, related, tags, status, version$nl  ☐ id: format [CODE]-[NNN] exactly — matches filename$nl  ☐ id: CODE is in Section 2 Category Code Registry$nl  ☐ id: NNN is correct next sequential number for this category$nl  ☐ title: exact keyword name — matches filename keyword portion$nl  ☐ category: matches Section 2 registry name exactly$nl  ☐ tier: correct tier folder name for this category$nl  ☐ folder: correct category folder name ([CODE]-descriptive)$nl  ☐ difficulty: exactly one of ★☆☆ ★★☆ ★★★$nl  ☐ depends_on: full IDs ([CODE]-[NNN]), not keyword names$nl  ☐ used_by: full IDs, not keyword names$nl  ☐ related: full IDs, not keyword names$nl  ☐ tags: # prefixed, comma-separated, from taxonomy (Section 4)$nl  ☐ status: one of draft / in-progress / complete$nl  ☐ version: integer, starts at 1"

if ($c.Contains($sec10_fm_old)) {
    $c = $c.Replace($sec10_fm_old, $sec10_fm_new)
    Write-Host "✅ Section 10 frontmatter checklist updated"
} else {
    Write-Host "❌ Section 10 NOT matched"
    Write-Host "Fragment check (FRONTMATTER:): $($c.Contains('FRONTMATTER:'))"
}

# ══════════════════════════════════════════════════════════════
# SECTION 11: prepend v3.0 changelog entry
# ══════════════════════════════════════════════════════════════

$sec11_anchor = "─────────────────────────────────────────────────────────────────────────$nl" +
                "v2.1 CHANGES (from v2.0)$nl" +
                "─────────────────────────────────────────────────────────────────────────"

$sec11_prepend = "─────────────────────────────────────────────────────────────────────────$nl" +
                 "ID SYSTEM v3.0 CHANGES (from embedded numeric IDs)$nl" +
                 "─────────────────────────────────────────────────────────────────────────$nl" +
                 "$nl" +
                 "SECTION 2: FILE FORMAT  →  ID SYSTEM, FILE FORMAT & FOLDER STRUCTURE$nl" +
                 "  - ID format changed: NNNN (global) → [CODE]-[NNN] (category-scoped)$nl" +
                 "  - IDs are PERMANENT and collision-proof by design$nl" +
                 "  - Category Code Registry added (50 categories, 9 tiers)$nl" +
                 "  - Folder structure: /tier-N-name/CODE-folder-name/ hierarchy$nl" +
                 "  - Wikilink format: [[CODE-NNN — Keyword Name]] full filename always$nl" +
                 "$nl" +
                 "SECTION 3: YAML FRONTMATTER  →  replaced Jekyll fields with:$nl" +
                 "  Removed: layout, parent, nav_order, permalink, number$nl" +
                 "  Added:   id, tier, folder, status, version$nl" +
                 "  Changed: depends_on / used_by / related now use full IDs (JVM-001)$nl" +
                 "           not keyword names; tags now # prefixed on one line$nl" +
                 "$nl" +
                 "SECTION 4: TAG TAXONOMY  →  added #angular, #gcp, #iac, #terraform,$nl" +
                 "  #async, #finance, #documents$nl" +
                 "$nl" +
                 "SECTION 9: INVOCATION  →  updated all commands to new ID format$nl" +
                 "  Added CROSS-CATEGORY BATCH command template$nl" +
                 "$nl" +
                 "SECTION 10: CHECKLIST  →  frontmatter validation updated to new fields$nl" +
                 "$nl" +
                 "─────────────────────────────────────────────────────────────────────────$nl" +
                 "v2.1 CHANGES (from v2.0)$nl" +
                 "─────────────────────────────────────────────────────────────────────────"

if ($c.Contains($sec11_anchor)) {
    $c = $c.Replace($sec11_anchor, $sec11_prepend)
    Write-Host "✅ Section 11 v3.0 changelog entry added"
} else {
    Write-Host "❌ Section 11 anchor NOT matched"
    Write-Host "Fragment check (v2.1 CHANGES): $($c.Contains('v2.1 CHANGES (from v2.0)'))"
}

# ══════════════════════════════════════════════════════════════
# SECTION 11: update header title
# ══════════════════════════════════════════════════════════════

$c = $c.Replace(
    'SECTION 11: CHANGE LOG — v1 → v2 → v2.1',
    'SECTION 11: CHANGE LOG — v1 → v2 → v2.1 → v3.0'
)
Write-Host "✅ Section 11 header updated"

# ══════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════

[System.IO.File]::WriteAllText($file, $c, $enc)
Write-Host "`n✅ ALL DONE. File saved. Length: $($c.Length)"
