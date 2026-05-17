---
agent: agent
description: "Generate keyword entries for a category or tier using Keyword Generator v4.0"
tools:
  - run_in_terminal
  - read_file
  - replace_string_in_file
  - create_file
  - list_dir
  - file_search
  - grep_search
---

# Keyword Generator - Category/Tier Processor

Generate keyword entries for a technology category or tier,
then sync the category `index.md` and create stub entry files.

**Target:** `${input:target:Category code (e.g. RCT, JVM, SEC) or tier folder (e.g. tier-3-java)}`

If the target is not a 3-letter category code or a `tier-N-name` folder,
stop and return an error that shows the valid formats.

---

## MASTER SPEC

The full keyword generation specification is in `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md`
(Category Keyword Generator - Master Prompt v4.0). Apply it exactly.

Keep the workflow linear and scoped: validate the target, scan the current
category state, generate only missing keywords, sync `index.md`, and create
stub files only when needed.

---

## Phase 0 - Resolve Target

Follow exactly one path. Do not combine paths.

**Step 1 — Identify input type:**

- Input is a 3-letter code (e.g. `RCT`, `JVM`, `SEC`) → **Path A: single category**
- Input is a tier folder (e.g. `tier-3-java`) → **Path B: entire tier**
- Input matches neither format → stop and return an error showing valid formats

**Path A — Single category:** Look up the code in the Category Code Registry and
proceed through Phases 1-6 once for that category.

**Path B — Entire tier:** List all category folders under `dictionary/{tier}/`,
extract the CODE from each folder name prefix, then run Phases 1-6 for each
category sequentially. Print a tier-level summary at the end.

**Step 2 — Look up registry fields** (for each category being processed)
from the Category Code Registry in `.github/instructions/dictionary.instructions.md`:

| Field         | Source                           |
| ------------- | -------------------------------- |
| CODE          | 3-letter category code           |
| CATEGORY_NAME | Full category name from registry |
| TIER          | Tier folder name (tier-N-name)   |
| FOLDER        | CODE-folder-name                 |
| INDEX_PATH    | dictionary/TIER/FOLDER/index.md  |

---

## Phase 1 - Scan Existing State

### 1a. Read existing index.md

```
Read: dictionary/{TIER}/{FOLDER}/index.md
```

Extract:

- **EXISTING_IDS**: every `CODE-NNN` ID in the keyword table
- **HIGHEST_ID**: the largest NNN sequence number
- **EXISTING_ROWS**: all table rows verbatim (these are IMMUTABLE)
- **EXISTING_COUNT**: total number of keyword rows
- **YAML_FRONTMATTER**: the complete YAML block (IMMUTABLE)
- **TITLE_HEADING**: the `# Category Name` line (IMMUTABLE)
- **DESCRIPTION_LINE**: the one-sentence description (IMMUTABLE)

If index.md does NOT exist, set HIGHEST_ID = 0 and EXISTING_COUNT = 0.

### 1b. Scan actual entry files in the folder

```
List: dictionary/{TIER}/{FOLDER}/*.md (excluding index.md)
```

For each entry file:

- Extract the `id:` from YAML frontmatter
- Extract the `title:` from YAML frontmatter
- Extract the `difficulty:` from YAML frontmatter
- Extract the `status:` from YAML frontmatter (draft/in-progress/complete)

Build a **FILE_INVENTORY**: set of all IDs that have actual .md files.

### 1c. Detect Sync Issues

Compare EXISTING_IDS (from index.md) vs FILE_INVENTORY (from folder scan):

| Situation                        | Action                                    |
| -------------------------------- | ----------------------------------------- |
| ID in index.md AND in folder     | Already synced - no action                |
| ID in folder but NOT in index.md | ORPHAN FILE - must add row to index.md    |
| ID in index.md but NOT in folder | MISSING FILE - flag but do NOT delete row |

Report all sync issues before proceeding.

---

## Phase 2 - Generate Keywords

Using `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md` v4.1 specification:

1. Set `Starting ID = CODE-{HIGHEST_ID + 1}` (or CODE-001 if new category)

   > **New category ID ordering:** When HIGHEST_ID = 0 (brand-new category), generate
   > all keywords grouped by difficulty before assigning IDs: produce every ★☆☆ keyword
   > first, then every ★★☆ keyword, then every ★★★ keyword. IDs are assigned in that
   > order (001 = first ★☆☆, ... N = last ★★★). This guarantees CODE-001 is always
   > the most foundational concept and learners progress naturally through the ID sequence.
   > **Existing categories:** append new keywords after HIGHEST_ID — do NOT re-sort.

2. Generate the complete keyword list for all applicable levels based on the category/tier.
   Include every level that is relevant to this technology domain:
   L0 (Orientation), L1 (Foundational), L2 (Working), L3 (Intermediate),
   L4 (Expert), L5 (Architect), L6 (Creator), META (Meta-Skills).
   **Relevance criteria:** Include a level if it has at least 3 meaningful keywords
   that a practitioner in this domain would need to know. Omit a level only if it
   produces fewer than 3 meaningful keywords for this specific category.
3. Apply ALL 24 rules from Section 2
4. Use ALL 12 output components from Section 3
5. Run ALL 18 quality checks from Section 4

**CRITICAL - New vs Missing keywords:**

- **Never create new content for IDs already in EXISTING_IDS.** These entries already
  exist; do not overwrite, duplicate, or regenerate them.
- **New keywords** = concepts not yet in EXISTING_IDS. Assign IDs starting from
  HIGHEST_ID + 1.
- **Gap Analysis** (when category has substantial coverage): scan by level (L0-META)
  to find levels with missing keywords. Generate ONLY the missing concepts as new
  IDs starting from HIGHEST_ID + 1. Do NOT modify existing ID assignments.

---

## Phase 3 - Sync Index.md (NON-DESTRUCTIVE)

> **NON-NEGOTIABLE SAFETY RULES** (from Section 3.10 of v4.0 spec).
> Apply these as a checklist - verify each before writing the file:
>
> - [ ] **NEVER** delete an existing keyword row from index.md
> - [ ] **NEVER** modify an existing keyword row's content
> - [ ] **NEVER** reorder existing rows
> - [ ] **NEVER** change the YAML frontmatter (layout, title, parent, nav_order, has_children, permalink)
> - [ ] **NEVER** change the title heading (breaks all child entry `parent:` references)
> - [ ] **ALWAYS** preserve exact whitespace, formatting, and content of existing rows
> - [ ] **ALWAYS** update the `**Keywords:**` count line to reflect the new total
> - [ ] **ALWAYS** assign new IDs starting from HIGHEST_ID + 1
> - [ ] **ALWAYS** place new rows AFTER all existing rows
> - [ ] If in doubt about ANY existing content: **DO NOT MODIFY IT**. Only append.

### 3a. Fix orphan files first

If Phase 1c found files in the folder that are NOT in index.md:

- Add their rows to the index.md table (after existing rows, in ID order)
- Use the file's frontmatter to build the row: `| CODE-NNN | Title | Difficulty |`

### 3b. Append new keyword rows

For each newly generated keyword:

- Add a row: `| CODE-NNN | Keyword Title | ★☆☆/★★☆/★★★ |`
- Append AFTER the last existing row (or after orphan-fix rows)
- Rows must be in ID order

### 3c. Update the Keywords count line

```
Old: **Keywords:** CODE-001-CODE-024 (24 terms)
New: **Keywords:** CODE-001-CODE-NNN (TOTAL terms)
```

Where NNN = highest ID, TOTAL = count of all rows in table.

### 3d. Create new index.md (if category is brand new)

If no index.md existed, create one using this template:

```yaml
---
layout: default
title: "Full Category Name"
parent: "Technical Dictionary"
nav_order: N
has_children: true
permalink: /category-slug/
---
```

```markdown
# Full Category Name

One-sentence description of this category.

**Keywords:** CODE-001-CODE-NNN (N terms)

| ID       | Keyword       | Difficulty |
| -------- | ------------- | ---------- |
| CODE-001 | First Keyword | ★☆☆        |
```

Rules:

- `title:` MUST match Category Name from registry EXACTLY
- `parent:` MUST be exactly `"Technical Dictionary"`
- `nav_order:` check existing categories, use next unique integer
- `permalink:` lowercase, hyphens only, unique across site
- Do NOT add `grand_parent:` to category index.md

---

## Phase 4 - Generate Stub Entry Files

For each NEW keyword (not already in FILE_INVENTORY):

### File naming

```
CODE-NNN - Keyword Name.md
```

> Separator is SPACE + HYPHEN + SPACE (`-`). NEVER em dash.

### Stub content

```markdown
---
id: CODE-NNN
title: Keyword Name
category: Full Category Name
tier: tier-N-name
folder: CODE-folder-name
difficulty: ★☆☆
depends_on:
used_by:
related:
tags:
  - tag1
  - tag2
status: draft
version: 0
layout: default
parent: "Full Category Name"
grand_parent: "Technical Dictionary"
nav_order: NNN
permalink: /category-slug/keyword-slug/
---

# CODE-NNN - Keyword Name

> Entry stub. Generate full content using Master Prompt v4.0.
```

Rules for stub files:

- `parent:` MUST exactly match the `title:` in the category index.md
- `grand_parent:` MUST be exactly `"Technical Dictionary"`
- `nav_order:` = the NNN sequence number (integer, no zero-padding)
- `permalink:` = lowercase, hyphens only, no special characters
- `difficulty:` = map from level (L0/L1 -> ★☆☆, L2/L3 -> ★★☆, L4/L5/L6 -> ★★★)
- `tags:` from approved taxonomy only
- `version:` = `0` (STUB_VERSION - never `1`; stubs have no generated body)
- `status: draft` (always draft for stubs)
- No BOM. UTF-8 encoding.

### File write safety

> **NEVER overwrite a file that has full content.**
>
> Before writing any stub file, check if the file already exists:
>
> - If the file exists AND has more than 20 lines: **SKIP IT** (it has content)
> - If the file exists AND has `status: complete` or `status: in-progress`: **SKIP IT**
> - If the file exists AND is a stub (< 20 lines, status: draft): safe to update
> - If the file does NOT exist: safe to create

---

## Phase 5 - Validate

After all changes, verify:

### Index.md integrity

- [ ] YAML frontmatter is unchanged from original
- [ ] No existing rows were modified or deleted
- [ ] All new keywords are present in the table
- [ ] Keywords count line matches actual table row count
- [ ] No duplicate IDs in the table
- [ ] `title:` matches what entries use as `parent:`

### File-Index sync

- [ ] Every .md file in the folder (except index.md) has a corresponding row in index.md
- [ ] Every row in index.md corresponds to an actual .md file in the folder
- [ ] ID range in `**Keywords:**` line matches first and last ID in table

### File integrity

- [ ] No files with full content were overwritten
- [ ] All new stubs have correct YAML frontmatter
- [ ] All new stubs have `status: draft`
- [ ] No em dashes anywhere in filenames or content
- [ ] File encoding is UTF-8 without BOM

Report validation results as a summary table.

---

## Phase 6 - Output Summary

Print a summary:

```
═══════════════════════════════════════════════════════════
KEYWORD GENERATION COMPLETE
═══════════════════════════════════════════════════════════

Category:       [Full Category Name]
Code:           [CODE]
Tier:           [tier-N-name]
Index file:     dictionary/[tier]/[FOLDER]/index.md

BEFORE:
  Existing keywords:  N
  Highest ID:         CODE-NNN

AFTER:
  Total keywords:     N
  Highest ID:         CODE-NNN
  New keywords added: N
  Orphans fixed:      N
  Stubs created:      N

FILES MODIFIED:
  - dictionary/[tier]/[FOLDER]/index.md  (updated)
  - dictionary/[tier]/[FOLDER]/CODE-NNN - Name.md  (created)
  ...

SYNC STATUS:  \u2713 Index and folder are in sync
\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550
```

---

## Quality Constitution (Non-Negotiable)

Keywords generated here will become full entries later. The keyword
list itself must be masterclass-quality: comprehensive, well-leveled,
with no gaps in coverage.

Full content quality spec: `dictionary/_config/GENERATOR_PROMPT.md` Section 7.

**Keyword List Quality Checks:**

- Every level (L0-META) covered where relevant (min 3 per level)
- No duplicate concepts across difficulty levels
- Each keyword represents a distinct, teachable concept
- Keywords progress from foundational to expert naturally
- Anti-patterns, decision frameworks, and failure modes included at L3+
- No vague/generic keywords ("Advanced Topics", "Best Practices")
- Each keyword name is specific enough to write a complete entry for

**When these stubs become entries, they MUST pass:**

1. Search Again? - reader never needs to look elsewhere
2. Feynman - smart beginner understands without confusion
3. Senior Engineer - senior still learns something useful
4. Staff Engineer - staff/principal respects this explanation
5. Production Reality - reader can diagnose real issues
6. Retention - reader remembers this next month
7. Decision - reader knows when to use or avoid
8. Scale - 10x/100x/1000x behavior covered

**Code Example Requirements (Non-Negotiable) - applied at content fill:**

Every concept with code must choose from these categories
(minimum 2-3 based on complexity):

1. Recognition Example - identify pattern in existing code
2. Wrong vs Right - MANDATORY (BAD before GOOD, always)
3. Production Example - real-world, not toy
4. Failure Example - MANDATORY - what breaks, symptoms, fix
5. Debugging Example - diagnostic commands, log analysis
6. Scale Example - what changes under load
7. Trade-off Example - gain vs sacrifice in code
8. Internal Mechanism Example - how it works underneath
9. System Interaction Example - cross-component behavior
10. Testing/Verification Example - prove correctness

Goal: reader understands why, when, failure, scale, debugging,
and trade-offs - not just the API.

---

## Encoding Safety (PowerShell)

When writing files via PowerShell scripts:

| Rule            | Correct                                         | Wrong                             |
| --------------- | ----------------------------------------------- | --------------------------------- |
| Interpreter     | `pwsh` (PowerShell 7+)                          | `powershell` (Windows PS 5.1)     |
| Output encoding | `[System.Text.UTF8Encoding]::new($false)`       | `[System.Text.Encoding]::UTF8`    |
| Script exec     | `pwsh -ExecutionPolicy Bypass -File script.ps1` | `powershell -ExecutionPolicy ...` |

---

## Multi-Category Mode (Tier Processing)

When target is a tier folder (e.g. `tier-3-java`):

1. List all category folders in `dictionary/{tier}/`
2. For each category folder, extract the CODE from folder name prefix
3. Process each category sequentially using Phases 1-6
4. Print a tier-level summary at the end showing all categories processed

---

## Quick Examples

**Single category - generate all keywords:**

```
Target: RCT
```

Generates missing keywords for React, updates index.md, creates stubs.

**Entire tier - process all categories:**

```
Target: tier-7-frontend
```

Processes HTM, CSS, JSC, TSC, RCT, ANG, NDJ, NPM, WBP sequentially.

**Category with existing keywords - gap fill:**

```
Target: JVM
```

Scans JVM-001 through JVM-066, identifies gaps per v3.0 rules,
generates only missing keywords starting from JVM-067.
