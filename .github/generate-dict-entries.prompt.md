---
mode: agent
description: "Generate Technical Dictionary keyword entries (Master Prompt v3.0) for a category or tier"
tools:
  - run_in_terminal
  - read_file
  - replace_string_in_file
---

# Technical Dictionary - Entry Generator

Generate complete, spec-compliant v3.0 keyword entries for all stub files in a **category** or **tier**.

**Target:** `${input:target:Category code (e.g. MSV, JVM) or tier number (e.g. 3, 5)}`
**Batch size:** `${input:batchSize:Entries per batch (default: 10)}`

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

## Phase 2 — Generate content for each batch

Work through **one batch at a time**. For each entry in the batch:

### 2a. Read the existing stub

Read the stub file to capture its exact frontmatter (id, title, nav_order, permalink, tags, depends_on, used_by, related, difficulty).

### 2b. Generate full v3.0 content

Apply every rule from the workspace `copilot-instructions.md` (already loaded). Key constraints:

**Structure** — YAML frontmatter plus all 22 content sections in order:

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
11. `### 📶 Gradual Depth - Four Levels`
12. `### ⚙️ How It Works (Mechanism)`
13. `### 🔄 The Complete Picture - End-to-End Flow`
14. `### 💻 Code Example` _(if programmatic)_
15. `### ⚖️ Comparison Table` _(if alternatives exist)_
16. `### 🔁 Flow / Lifecycle` _(if multi-phase lifecycle)_
17. `### ⚠️ Common Misconceptions` _(min 4 rows)_
18. `### 🚨 Failure Modes & Diagnosis` _(min 3 modes)_
19. `### 🔗 Related Keywords`
20. `### 📌 Quick Reference Card`
21. `### 💎 Transferable Wisdom`
22. `### 💡 The Surprising Truth`
23. `### 🧠 Think About This Before We Continue` (3 Qs with _Hint:_ per question)

**Formatting rules:**

- Every `###` preceded by `---` (blank line before and after both)
- ASCII diagrams ≤59 chars wide; code lines ≤70 chars
- BAD pattern shown **before** GOOD pattern in code examples
- `← YOU ARE HERE` marker in the normal flow diagram

**YAML rules:**

- Preserve all existing frontmatter fields (id, nav_order, permalink, tags)
- Add or update: `status: complete`, `version: 1`
- Double-quote any `title:` containing `: ` (colon + space)
- Use full IDs for `depends_on`, `used_by`, `related` (e.g. `MSV-006, DST-001`)
- No em dashes (`—`) anywhere — use hyphens (`-`)

### 2c. Write the file

Replace the entire stub content with the generated v3.0 entry.

### 2d. Confirm

After writing each batch, confirm the files were saved successfully before continuing to the next batch.

---

## Phase 3 — Commit

After all batches are written:

```powershell
cd C:\ASK\MyWorkspace\sk-keys
git add dictionary/
git commit -m "feat: generate ${input:target} entries - full v3.0 content"
```

---

## Quality checklist (verify before committing)

```powershell
& "C:\Users\skurremula\.local\bin\python3.14.exe" `
  tmp/check_all_categories.py `
  --category "${input:target}" `
  --v3-only
```

All generated entries should show `v3.0` and `complete`. If any show otherwise, fix before committing.
