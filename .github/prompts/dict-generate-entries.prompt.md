---
agent: agent
description: "Generate or upgrade Technical Dictionary keyword entries to LATEST_VERSION_LABEL for a category or tier"
tools:
  - run_in_terminal
  - read_file
  - replace_string_in_file
---

# Technical Dictionary - Entry Generator (LATEST_VERSION_LABEL)

> **Version Registry** — `LATEST_VERSION` = **4** | `LATEST_VERSION_LABEL` = **v4.0** | `STUB_VERSION` = **0**
> _To release v5: update the Version Registry in `.github/copilot-instructions.md`, `.github/instructions/dictionary.instructions.md`, and `dictionary/_config/GENERATOR_PROMPT.md`, rename `upgrade_to_v4.ps1` to `upgrade_to_v5.ps1`, then update this file's commit messages and script references._

Generate complete, spec-compliant **LATEST_VERSION_LABEL** keyword entries for stub files in either a specific **category** (e.g. `MSV`, `JVM`) or a specific **tier** (e.g. `3`, `5`) — but not both simultaneously. A category targets one folder; a tier targets all categories within that tier number.
or upgrade existing older entries by adding missing LATEST_VERSION_LABEL sections.

**Target:** `${input:target:Category code (e.g. MSV, JVM) or tier number (e.g. 3, 5)}`
**Batch size:** `${input:batchSize:Entries per batch (default: 10)}`
**Mode:** `${input:mode:generate (default) | upgrade}`

> **Input validation:** If `target` is not a recognized 3-letter category code or a single digit tier number (1-9), stop and report: `"Invalid target '${input:target}'. Provide a category code (e.g. MSV, JVM) or a tier number (1-9)."` If `batchSize` is not a positive integer, default to `10`.

> **Default mode is `generate`** — always produces full LATEST_VERSION_LABEL entries (`version: LATEST_VERSION`, currently `4`).
> Use `upgrade` to surgically add missing LATEST_VERSION_LABEL sections to existing older files.

---

## Phase 0 — Show version statistics

Before doing anything, run the upgrade script in stats-only mode to understand the current state:

```powershell
cd C:\ASK\MyWorkspace\sk-keys
pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Category "${input:target}"
# --- OR for a tier ---
# pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Tier "${input:target}"
```

Read the output. It shows:

- Count of files at each version level (v0 stubs → v4 complete)
- Number of files eligible for upgrade (v1+v2+v3)

If all files are already `version: LATEST_VERSION` (currently `4`), stop — nothing to do.

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

## Phase 2 — Generate full LATEST*VERSION_LABEL content *(generate mode only)\_

Work **one batch at a time**. For each stub entry:

### 2a. Read the stub

Read the file to capture its exact frontmatter: `id`, `title`, `nav_order`, `permalink`, `tags`,
`depends_on`, `used_by`, `related`, `difficulty`.

### 2b. Generate complete v4.0 entry

Apply every rule from `.github/instructions/dictionary.instructions.md` (auto-loaded) and `dictionary/_config/GENERATOR_PROMPT.md` (full spec). Rules are grouped into four categories - Content, Conditional sections, Formatting, YAML - applied in that priority order. **All 24 sections are required in order.** If a conditional section's condition is not met, omit the entire section and all its subsections. For all other rules, apply them as specified without omission. Conditional section decisions follow the decision table in the dictionary instructions:

| #    | Section                                         | Notes                                                             |
| ---- | ----------------------------------------------- | ----------------------------------------------------------------- |
| FM   | YAML frontmatter                                | `status: complete`, `version: LATEST_VERSION` (currently `4`)     |
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
| 5.24 | `### 🎯 Interview Deep-Dive`                    | 3-7 Qs scaled by difficulty; scenario-based; tests experience     |

**Critical rules — apply in this sequence for every entry:**

**Step 1 — Formatting rules:**

- Every `###` must be preceded by `---` (blank line before and after both)
- ASCII diagrams ≤59 chars wide; code lines ≤70 chars
- BAD pattern always before GOOD pattern in code examples
- No H2 (`##`) headers in body
- No em dashes — use hyphens

**Step 2 — YAML rules:**

- Preserve all existing frontmatter fields (`id`, `nav_order`, `permalink`, `tags`)
- Always set: `status: complete`, `version: LATEST_VERSION` (currently `4`)
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

Replace the entire stub content with the generated LATEST_VERSION_LABEL entry. Use UTF-8 without BOM.

### 2d. Confirm and continue

After each batch: confirm saves succeeded, then proceed to the next batch without pausing.

---

## Phase 2U — Upgrade older entries → LATEST*VERSION_LABEL *(upgrade mode only)\_

**Use the dedicated upgrade script** — it adds only missing LATEST_VERSION_LABEL sections; existing content is untouched:

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
2. Add `### 🎯 Interview Deep-Dive` section (if absent) — with TODO placeholders
3. Add `**Industry applications:**` to Transferable Wisdom (if absent) — with TODO placeholders
4. Add Level 5 stub to Gradual Depth (if only Four Levels found)
5. Set `version: LATEST_VERSION` (currently `4`) in frontmatter

**After the script runs**, search upgraded files for `<!-- TODO LATEST_VERSION_LABEL:` and fill each stub using Copilot,
reading the entry's existing content for context. Add only the missing content — do not rewrite existing sections. If an existing section partially meets LATEST_VERSION_LABEL requirements, adjust only the non-compliant parts to bring it into full compliance.

---

## Phase 3 - Commit

Commit in batches of **10 created files** (non-negotiable):

```powershell
cd C:\ASK\MyWorkspace\sk-keys
git add dictionary/
# generate mode:
git commit -m "feat: generate ${input:target} <CODE>-<START>-<CODE>-<END> - batch <N>"
# upgrade mode:
# git commit -m "upgrade: ->LATEST_VERSION_LABEL ${input:target} <CODE>-<START>-<CODE>-<END> - batch <N>"
```

**Batch Rules:**

- Do NOT commit single files - wait until 10 files are created
- Only count **created** files (not just modified)
- If fewer than 10 remain at the end, commit all remaining
- Do NOT `git push`

---

## Phase 4 — Verify

Run final stats to confirm progress:

```powershell
pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Category "${input:target}"
```

All generated entries should show `version: LATEST_VERSION` (currently `4`) and `status: complete`.

---

## Quality Constitution (Non-Negotiable)

Every generated entry MUST pass ALL eight quality tests.
Full spec: `dictionary/_config/GENERATOR_PROMPT.md` Section 7.

**Voice:** Precise like Josh Bloch. Clear like Martin Fowler. Intuitive like
Feynman. Production-scarred like a senior systems architect.

**Eight Tests (all must pass):**

1. Search Again? - reader never needs to look elsewhere
2. Feynman - smart beginner understands without confusion
3. Senior Engineer - senior still learns something useful
4. Staff Engineer - staff/principal respects this explanation
5. Production Reality - reader can diagnose real issues
6. Retention - reader remembers this next month
7. Decision - reader knows when to use or avoid
8. Scale - 10x/100x/1000x behavior covered

**Code Example Requirements (Non-Negotiable):**

Every concept with code - choose based on complexity (min 2-3):

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

**10-Point Writing Standard:**
Intuition, Mechanism, Trade-off, Failure, Diagnosis, Scale,
Decision, Memory, Transfer, Reality

**Forbidden:** Generic definitions, toy examples, vague advice,
fabricated numbers, surface explanations, "best practice" without
reasoning, walls of prose, repetition across sections.

**Final Gate:** "Would an experienced engineer say 'Damn - this is
genuinely excellent'?" If uncertain: rewrite. Masterclass = target.
