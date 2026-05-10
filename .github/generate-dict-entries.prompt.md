---
agent: agent
description: "Generate or upgrade Technical Dictionary keyword entries to v4.0 for a category or tier"
tools:
  - run_in_terminal
  - read_file
  - replace_string_in_file
---

# Technical Dictionary - Entry Generator (v4.0)

Generate complete, spec-compliant **v4.0** keyword entries for stub files in a **category** or **tier**,
or upgrade existing v1/v2/v3 entries by adding missing v4 sections.

**Target:** `${input:target:Category code (e.g. MSV, JVM) or tier number (e.g. 3, 5)}`
**Batch size:** `${input:batchSize:Entries per batch (default: 10)}`
**Mode:** `${input:mode:generate (default) | upgrade}`

> **Default mode is `generate`** — always produces full v4.0 entries (`version: 4`).
> Use `upgrade` to surgically add missing v4 sections to existing v1/v2/v3 files.

---

## Phase 0 — Show version statistics

Before doing anything, run the upgrade script in stats-only mode to understand the current state:

```powershell
cd C:\ASK\MyWorkspace\sk-keys
pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Category "${input:target}"
# Or for a tier:
# pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Tier "${input:target}"
```

Read the output. It shows:

- Count of files at each version level (v0 stubs → v4 complete)
- Number of files eligible for upgrade (v1+v2+v3)

If all files are already `v4`, stop — nothing to do.

---

## Phase 1 — Discover work items

**For `generate` mode** — find stub files (version 0) that need full content:

```powershell
& "C:\Users\skurremula\.local\bin\python3.14.exe" `
  tmp/generate_queue.py `
  --target "${input:target}" `
  --batch-size "${input:batchSize}"
```

If output says **"Nothing to generate"**, all stubs are filled — switch to `upgrade` mode or stop.

**For `upgrade` mode** — the upgrade script already listed eligible files in Phase 0.

---

## Phase 2 — Generate full v4.0 content _(generate mode only)_

Work **one batch at a time**. For each stub entry:

### 2a. Read the stub

Read the file to capture its exact frontmatter: `id`, `title`, `nav_order`, `permalink`, `tags`,
`depends_on`, `used_by`, `related`, `difficulty`.

### 2b. Generate complete v4.0 entry

Apply every rule from the loaded `copilot-instructions.md`. **All 23 sections are required in order:**

| #    | Section                                         | Notes                                                             |
| ---- | ----------------------------------------------- | ----------------------------------------------------------------- |
| FM   | YAML frontmatter                                | `status: complete`, `version: 4`                                  |
| 5.1  | `# CODE-NNN - KEYWORD NAME`                     |                                                                   |
| 5.2  | ⚡ TL;DR ≤25 words                              | WHY + WHAT                                                        |
| 5.3  | Metadata table                                  | Depends on / Used by / Related rows                               |
| 5.4  | `### 🔥 The Problem This Solves`                | includes `**EVOLUTION:**`                                         |
| 5.5  | `### 📘 Textbook Definition`                    |                                                                   |
| 5.6  | `### ⏱️ Understand It in 30 Seconds`            | 3 parts: One line / One analogy / One insight                     |
| 5.7  | `### 🔩 First Principles Explanation`           | CORE INVARIANTS + TRADE-OFFS + ESSENTIAL vs ACCIDENTAL            |
| 5.8  | `### 🧪 Thought Experiment`                     | SETUP / WITHOUT / WITH / INSIGHT                                  |
| 5.9  | `### 🧠 Mental Model / Analogy`                 | blockquote + mapping + breakdown note                             |
| 5.10 | `### 📶 Gradual Depth - Five Levels`            | L1 anyone → L5 distinguished (all 5 required)                     |
| 5.11 | `### ⚙️ How It Works (Mechanism)`               |                                                                   |
| 5.12 | `### 🔄 The Complete Picture - End-to-End Flow` | `← YOU ARE HERE` marker required                                  |
| 5.13 | `### 💻 Code Example`                           | if programmatic; BAD before GOOD                                  |
| 5.14 | `### ⚖️ Comparison Table`                       | if alternatives exist                                             |
| 5.15 | `### 🔁 Flow / Lifecycle`                       | only if multi-phase lifecycle                                     |
| 5.16 | `### ⚠️ Common Misconceptions`                  | min 4 rows                                                        |
| 5.17 | `### 🚨 Failure Modes & Diagnosis`              | min 3 modes; at least 1 security mode if applicable               |
| 5.18 | `### 🔗 Related Keywords`                       | 3 categories: Prerequisites / Builds On / Alternatives            |
| 5.19 | `### 📌 Quick Reference Card`                   | 9-row box including ANTI-PATTERN row + Remember 3 + Interview     |
| 5.20 | `### 💎 Transferable Wisdom`                    | Principle + 3 where-else + **Industry applications:** (2 bullets) |
| 5.21 | `### 💡 The Surprising Truth`                   | 1 counterintuitive fact                                           |
| 5.22 | `### ✅ Mastery Checklist`                      | 5 indicators: EXPLAIN / DEBUG / DECIDE / BUILD / EXTEND           |
| 5.23 | `### 🧠 Think About This Before We Continue`    | 3 Qs + Hint each; at least 1 TYPE G                               |

**Critical formatting rules (enforce on every entry):**

- Every `###` must be preceded by `---` (blank line before and after both)
- ASCII diagrams ≤59 chars wide; code lines ≤70 chars
- BAD pattern always before GOOD pattern in code examples
- No H2 (`##`) headers in body
- No em dashes — use hyphens

**Critical YAML rules:**

- Preserve all existing frontmatter fields (`id`, `nav_order`, `permalink`, `tags`)
- Always set: `status: complete`, `version: 4`
- Double-quote any `title:` containing `: ` (colon + space)
- Full IDs for `depends_on`, `used_by`, `related` (e.g. `MSV-006, DST-001`)

**Size calibration (P13):**

| Concept type                      | Target word count |
| --------------------------------- | ----------------- |
| Tiny / single-purpose             | 800–1 200         |
| Medium / one mechanism            | 1 500–3 000       |
| Foundational / widely depended on | 4 000–7 000       |
| Deep-dive architecture            | 7 000–12 000      |

### 2c. Write the file

Replace the entire stub content with the generated v4.0 entry. Use UTF-8 without BOM.

### 2d. Confirm and continue

After each batch: confirm saves succeeded, then proceed to the next batch without pausing.

---

## Phase 2U — Upgrade v1/v2/v3 → v4.0 _(upgrade mode only)_

**Use the dedicated upgrade script** — it adds only missing v4 sections; existing content is untouched:

```powershell
cd C:\ASK\MyWorkspace\sk-keys

# Upgrade next 10 eligible files in a category:
pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 `
     -Upgrade -Category "${input:target}" -BatchSize "${input:batchSize}"

# Or for a tier:
# pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 `
#      -Upgrade -Tier "${input:target}" -BatchSize "${input:batchSize}"
```

The script will:

1. Add `### ✅ Mastery Checklist` section (if absent) — with TODO placeholders
2. Add `**Industry applications:**` to Transferable Wisdom (if absent) — with TODO placeholders
3. Add Level 5 stub to Gradual Depth (if only Four Levels found)
4. Set `version: 4` in frontmatter

**After the script runs**, search upgraded files for `<!-- TODO v4.0:` and fill each stub using Copilot,
reading the entry's existing content for context. Add only the missing content — do not rewrite existing sections.

---

## Phase 3 — Commit

After all batches complete:

```powershell
cd C:\ASK\MyWorkspace\sk-keys
git add dictionary/
# generate mode:
git commit -m "feat: generate ${input:target} entries - full v4.0 content"
# upgrade mode:
# git commit -m "upgrade: ->v4.0 ${input:target} entries - batch N"
```

---

## Phase 4 — Verify

Run final stats to confirm progress:

```powershell
pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Category "${input:target}"
```

All generated entries should show `version: 4` and `status: complete`.
