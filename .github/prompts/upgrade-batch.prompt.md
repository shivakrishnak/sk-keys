---
mode: agent
description: Upgrade sk-keys dictionary entries to v4.0 - scaffold + fill content
---

# Upgrade Batch - sk-keys Technical Dictionary

You are upgrading sk-keys Technical Dictionary entries to **v4.0 standard**.
The full spec is in `copilot-instructions.md` (already loaded as workspace instructions).

## How to invoke

```
@upgrade-batch  CODE=DST  START=066  END=070
@upgrade-batch  CODE=JVM  START=037  END=041
```

## Workflow (execute in order, no confirmation needed between steps)

### Step 1 — Check current status

```bash
python tmp/check_all_categories.py --category {{CODE}} --v3-only
```

This shows which files in the range are not yet v4.0 complete.

### Step 2 — Generate scaffolds

```bash
python tmp/generate_scaffold.py {{CODE}} {{START}} {{END}}
```

This writes each file with correct YAML + all 23 section stubs.
Only files that are NOT already v4.0 complete need content filled in.

> ⚠️ **Encoding rule — enforced at every file write:**
> When writing via PowerShell PS1 scripts, ALWAYS use `pwsh` (not `powershell`) and
> `[System.Text.Encoding]::new('utf-8')` (not `::UTF8`). Using `powershell.exe` or
> `::UTF8` corrupts emoji (`⚡` → `âš¡`, `★` → `â˜…`) and adds a BOM that breaks
> YAML frontmatter. See copilot-instructions.md §Encoding Safety for full details.

### Step 3 — Fill content stubs (one file at a time)

For each scaffolded file:

1. Read the file (first 30 lines to see YAML, then skim for [FILL] stubs)
2. Replace ALL `[FILL:...]` stubs with full v4.0 content per spec
3. Follow copilot-instructions.md rules exactly:
   - Every `###` preceded by `---` with blank lines before and after both
   - ASCII diagrams ≤59 chars wide; code lines ≤70 chars
   - BAD pattern before GOOD pattern in code examples
   - Min 4 misconception rows; min 3 failure modes (at least 1 security)
   - 3 Think questions (types A/B/C/D/E/F/G), each with `*Hint:*`, at least 1 TYPE G
   - Tags from approved taxonomy only
   - Section 5.15 (Flow/Lifecycle): include ONLY if multi-phase lifecycle exists
   - `depends_on` / `used_by` / `related`: full IDs only (CODE-NNN)
   - 5 Gradual Depth levels (Level 5 = Mastery for distinguished engineers)
   - Quick Reference Card: 9 rows (includes ANTI-PATTERN)
   - Mastery Checklist: 5 testable indicators (EXPLAIN/DEBUG/DECIDE/BUILD/EXTEND)
   - Transferable Wisdom: includes **Industry applications:**

Use `replace_string_in_file` to replace each stub with actual content.
Complete one file fully before moving to the next.

### Step 4 — Verify

```bash
python tmp/check_all_categories.py --category {{CODE}} --v3-only
```

All files in the batch should now show `v4.0 / complete`.
H1 count should be 1 per file.

### Step 5 — Commit

```bash
git add dictionary/{{TIER}}/{{FOLDER}}/
git commit -m "upgrade: ->v4.0 {{CODE}}-{{START}}-{{CODE}}-{{END}} {{CATEGORY_NAME}} - batch {{BATCH_N}}"
```

Do NOT `git push`.

## Content quality rules (non-negotiable)

| Rule                 | Detail                                                                    |
| :------------------- | :------------------------------------------------------------------------ |
| North Star           | If the reader must look elsewhere to understand: entry has failed         |
| TL;DR                | Max 25 words, essence + WHY, no jargon                                    |
| Analogies            | Blockquote only in section 5.9; everyday object, not another tech concept |
| Thought Experiment   | One scenario that makes the concept impossible to misunderstand           |
| Failure modes        | Real diagnostic commands (`nodetool`, `kubectl`, `aws cli`, etc.)         |
| Code examples        | Always BAD then GOOD, always labelled, always test/verify at end          |
| Think questions      | Must NOT be answerable from the entry alone; hint points WHERE to look    |
| The Surprising Truth | ONE fact, 2-4 sentences, factually accurate, genuinely counterintuitive   |
| Transferable Wisdom  | One principle + 3 real-world domains where it appears                     |

## Common mistakes to avoid

- Using unapproved tags (e.g. `replication`, `consistency`, `repair`)
- Em dashes (`—`) anywhere in the file — use hyphen (`-`)
- `parent:` value not matching index.md title exactly
- Missing blank line before/after `---` separators
- Section 5.15 included when there is no distinct lifecycle
- `depends_on` with keyword names instead of CODE-NNN IDs
- ASCII diagrams wider than 59 characters
- Running PS1 scripts with `powershell` instead of `pwsh` (corrupts emoji)
- Using `[System.Text.Encoding]::UTF8` instead of `::new('utf-8')` (adds BOM)
