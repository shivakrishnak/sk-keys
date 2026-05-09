---
mode: agent
description: "Generate Technical Dictionary keyword entries (Master Prompt v4.0) for a category or tier"
tools:
  - run_in_terminal
  - read_file
  - replace_string_in_file
---

# Technical Dictionary - Entry Generator

Generate complete, spec-compliant v4.0 keyword entries for all stub files in a **category** or **tier**.

**Target:** `${input:target:Category code (e.g. MSV, JVM) or tier number (e.g. 3, 5)}`
**Batch size:** `${input:batchSize:Entries per batch (default: 10)}`
**Mode:** `${input:mode:generate (default) | upgrade-v40}`

---

## Phase 1 — Discover stubs

Run the queue generator to find all stub entries that need content:

```powershell
& "C:\Users\skurremula\.local\bin\python3.14.exe" `
  tmp/generate_queue.py `
  --target "${input:target}" `
  --batch-size "${input:batchSize}"
```

Read the output carefully. It lists every stub file grouped into batches, with:

- Entry ID (`CODE-NNN`)
- Title
- Difficulty
- Category name, tier, folder

If the output says **"Nothing to generate"**, stop here — all entries are complete.

---

## Phase 2 — Generate content for each batch _(skip when mode = upgrade-v40)_

Work through **one batch at a time**. For each entry in the batch:

### 2a. Read the existing stub

Read the stub file to capture its exact frontmatter (id, title, nav_order, permalink, tags, depends_on, used_by, related, difficulty).

### 2b. Generate full v4.0 content

Apply every rule from the workspace `copilot-instructions.md` (already loaded). Key constraints:

**Structure** — YAML frontmatter plus all 23 content sections in order:

1. YAML frontmatter (update `status: draft` → `status: complete`)
2. `# CODE-NNN - KEYWORD NAME`
3. ⚡ TL;DR (≤25 words)
4. Metadata table (Depends on / Used by / Related)
5. `### 🔥 The Problem This Solves` — includes `**EVOLUTION:**`
6. `### 📘 Textbook Definition`
7. `### ⏱️ Understand It in 30 Seconds`
8. `### 🔩 First Principles Explanation`
9. `### 🧪 Thought Experiment`
10. `### 🧠 Mental Model / Analogy`
11. `### 📶 Gradual Depth - Five Levels`
12. `### ⚙️ How It Works (Mechanism)`
13. `### 🔄 The Complete Picture - End-to-End Flow`
14. `### 💻 Code Example` _(if programmatic)_
15. `### ⚖️ Comparison Table` _(if alternatives exist)_
16. `### 🔁 Flow / Lifecycle` _(if multi-phase lifecycle)_
17. `### ⚠️ Common Misconceptions` _(min 4 rows)_
18. `### 🚨 Failure Modes & Diagnosis` _(min 3 modes)_
19. `### 🔗 Related Keywords`
20. `### 📌 Quick Reference Card` _(9-row box with ANTI-PATTERN row)_
21. `### 💎 Transferable Wisdom` _(principle + 3 apps + industry)_
22. `### 💡 The Surprising Truth`
23. `### ✅ Mastery Checklist` _(5 testable indicators)_
24. `### 🧠 Think About This Before We Continue` _(3 Qs with Hint, at least 1 TYPE G)_

**Formatting rules:**

- Every `###` preceded by `---` (blank line before and after both)
- ASCII diagrams ≤59 chars wide; code lines ≤70 chars
- BAD pattern shown **before** GOOD pattern in code examples
- `← YOU ARE HERE` marker in the normal flow diagram

**YAML rules:**

- Preserve all existing frontmatter fields (id, nav_order, permalink, tags)
- Add or update: `status: complete`, `version: 3`
- Double-quote any `title:` containing `: ` (colon + space)
- Use full IDs for `depends_on`, `used_by`, `related` (e.g. `MSV-006, DST-001`)
- No em dashes (`—`) anywhere — use hyphens (`-`)

**Size rules (P13 — Cognitive Load Budgeting):**

- Tiny concepts (single-purpose, atomic): 800–1200 words
- Medium concepts (one mechanism, clear boundaries): 1500–3000 words
- Foundational concepts (multi-faceted, widely depended on): 4000–7000 words
- Deep-dive architecture concepts (system-spanning): 7000–12000 words
- Every paragraph must justify its presence. If removing it loses nothing, remove it.

### 2c. Write the file

Replace the entire stub content with the generated v4.0 entry.

### 2d. Confirm

After writing each batch, confirm the files were saved successfully before continuing to the next batch.

---

## Upgrade Phase — v3.0 → v3.1 _(only when mode = upgrade-v31; replaces Phase 2)_

Work through one batch at a time. For each entry in the batch:

### U-i. Identify upgrade candidates

Read each file. A valid v3.0 upgrade candidate has:

- `id:` field in YAML frontmatter (format `CODE-NNN`)
- `status:` and `version:` fields present
- All 7 v3.0 structural section markers present:
  `### 🔥 The Problem This Solves` · `### ⏱️ Understand It in 30 Seconds` ·
  `### 🧪 Thought Experiment` · `### 💶 Gradual Depth - Four Levels` ·
  `### 🔄 The Complete Picture - End-to-End Flow` ·
  `### ⚖️ Comparison Table` · `### 🚨 Failure Modes & Diagnosis`

Skip any file where `version:` is already `2` or higher (already v3.1).

### U-ii. Apply v3.1 quality improvements

Read the full file content, then apply each check in order:

**1. Cognitive load audit (P13):**

- Estimate word count. Is length proportional to concept complexity?
  - Tiny concept (single-purpose, atomic) → target ≤1500 words. Trim redundant prose.
  - Deep-dive architecture → ensure ≥4000 words; add depth only where genuinely missing.
- Remove any paragraph that repeats a point already made in the same section.
- Do NOT pad entries — only trim or fill genuine content gaps.

**2. Truthfulness review:**

- Find any specific latency numbers, throughput figures, or scalability claims stated as fact without hedging.
- Add qualifiers where certainty is unavailable: `implementation-dependent`, `typically`, `commonly observed`, `varies by runtime/version`.
- Reframe any production stories that read as fabricated (generic company names, suspiciously perfect incident arcs).
- Do not remove accurate, well-established, verifiable facts.

**3. Deduplication review:**

- Identify explanations that re-cover ground already in prerequisite entries listed in `depends_on`.
- Replace re-explanations with: _"As covered in `[[CODE-NNN - Keyword]]`, [one bridging sentence]."_
- Keep only what is unique to this concept’s perspective.

**4. Version Evolution table (conditional):**

- Is this concept an evolving technology (language feature, framework capability, runtime behaviour)?
  - YES → Add a `**Version Evolution:**` table inside the `**EVOLUTION:**` sub-section of `### 🔥 The Problem This Solves`.
  - NO (algorithm, data structure, architectural pattern, timeless principle) → skip entirely.
- Table format: `| Version | What Changed | Why It Matters |`

**5. Decision Tree (conditional):**

- Does `### ⚖️ Comparison Table` have 3+ rows AND the choice involves 3+ distinct engineering conditions?
  - YES → Add a `**Decision Tree:**` block immediately below the “How to choose” note.
  - NO (2-option comparison, or simple trade-off table) → skip entirely.
- Format: `Need [condition]? → Choose X`

### U-iii. Update frontmatter

- Increment `version:` by 1 (e.g. `version: 1` → `version: 2`)
- Do NOT change `id`, `nav_order`, `permalink`, `status`, `tags`, or any other field.

### U-iv. Write the file

Overwrite the existing file with the v3.1-upgraded content. Preserve the same filename and path.

### U-v. Confirm

After each file, confirm the write succeeded and note which v3.1 improvements were applied (cognitive trim / truthfulness hedges / dedup refs / version table / decision tree).

---

## Phase 3 — Commit

After all batches are written:

```powershell
cd C:\ASK\MyWorkspace\sk-keys
git add dictionary/
# For generate mode:
git commit -m "feat: generate ${input:target} entries - full v4.0 content"
# For upgrade-v40 mode:
# git commit -m "upgrade: →v4.0 ${input:target} entries - batch N"
```

---

## Quality checklist (verify before committing)

```powershell
& "C:\Users\skurremula\.local\bin\python3.14.exe" `
  tmp/check_all_categories.py `
  --category "${input:target}" `
  --v3-only
```

All generated entries should show `complete`. For upgrade-v40 mode, confirm `version: 3` is set on upgraded files. If any show otherwise, fix before committing.
