---
agent: agent
description: Upgrade sk-keys technical-mastery entries to v6.0 - scaffold + fill content
---

# Upgrade Batch - sk-keys Technical Mastery

You are upgrading sk-keys Technical Mastery entries to **v6.0 standard**.
The full spec is in `.github/instructions/technical-mastery.instructions.md` (auto-loaded for dictionary files)
and `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md` (complete spec).

## How to invoke

Use one target at a time: pass either `CODE` alone (no `START`/`END`) to process the full category, or `CODE` with `START` and `END` to process a specific range. If `START` is provided without `END` (or vice versa), reject the input and return an error specifying which parameter is missing.

> **Input validation:** If `CODE` is missing or not a recognized 3-letter category code, stop and report: `"Invalid CODE '{{CODE}}'. Provide a valid 3-letter category code (e.g. DST, JVM)."` If using range mode and `START` or `END` are missing or not 3-digit numbers, stop and report the issue before proceeding.

> **TECHNICAL_MASTERY_LIST.md RULE:** This prompt generates entry content
> only - not keyword lists. You MAY read `TECHNICAL_MASTERY_LIST.md` to
> understand what topics the target category covers or to cross-check
> peer category structures. Do NOT copy or derive new keyword titles
> from it - that is the job of `@technical-mastery-generate-keywords`. If keyword
> coverage is missing for a category, run `@technical-mastery-generate-keywords` first.

```
@upgrade-batch  CODE=DST  START=066  END=070
@upgrade-batch  CODE=JVM  START=037  END=041
```

**Constraint priority order:** Input validation -> Formatting rules -> Content minimums -> YAML and references -> Quality tests.

## Workflow (execute in order, no confirmation needed between steps)

**Steps:** 1 (check status) -> 2 (scaffold) -> 3 (fill content) -> 4 (verify) -> 5 (commit). Complete one file fully in Step 3 before moving to the next.

### Step 1 — Check current status

```bash
python tmp/check_all_categories.py --category {{CODE}} --v3-only
```

This shows which files in the range are not yet v6.0 complete.

### Step 2 — Generate scaffolds

```bash
python tmp/generate_scaffold.py {{CODE}} {{START}} {{END}}
```

This writes each file with correct YAML + all 24 section stubs.
Only files that are NOT already v6.0 complete need content filled in.

> ⚠️ **Encoding rule — enforced at every file write:**
> When writing via PowerShell PS1 scripts, ALWAYS use `pwsh` (not `powershell`) and
> `[System.Text.Encoding]::new('utf-8')` (not `::UTF8`). Using `powershell.exe` or
> `::UTF8` corrupts emoji (`⚡` → `âš¡`, `★` → `â˜…`) and adds a BOM that breaks
> YAML frontmatter. See `.github/instructions/technical-mastery.instructions.md` §Encoding Safety for full details.

### Step 3 — Fill content stubs (one file at a time)

For each scaffolded file:

1. Read the file (first 30 lines to see YAML, then skim for [FILL] stubs)
2. Replace ALL `[FILL:...]` stubs with full v6.0 content per spec
3. Apply dictionary spec rules using this grouped checklist:

   **Formatting:**
   - Every `###` preceded by `---` with blank lines before and after both
   - ASCII diagrams ≤59 chars wide; code lines ≤70 chars
   - Diagrams: DUAL format (ASCII first, then Mermaid below). Types: flowchart, sequenceDiagram, stateDiagram-v2, classDiagram, erDiagram, mindmap
   - BAD pattern before GOOD pattern in code examples
   - No `# H1` in body - Just the Docs renders H1 from YAML `title`
   - Bold-label lines (`**LABEL:** value`) separated by blank lines

   **Content minimums:**
   - Min 4 misconception rows; min 3 failure modes (at least 1 security)
   - 3 Think questions (types A/B/C/D/E/F/G), each with `*Hint:*`, at least 1 TYPE G
   - 5 Gradual Depth levels (Level 5 = Mastery for distinguished engineers)
   - Mastery Checklist: 5 testable indicators (EXPLAIN/DEBUG/DECIDE/BUILD/EXTEND)
   - Quick Reference Card: 9 rows (includes ANTI-PATTERN)
   - Transferable Wisdom: includes **Industry applications:**

   **YAML & references:**
   - Tags from approved taxonomy only
   - `depends_on` / `used_by` / `related`: full IDs only (CODE-NNN)

   **Conditional sections:**
   - Section 5.15 (Flow/Lifecycle): include ONLY if multi-phase lifecycle exists

Use `replace_string_in_file` to replace each stub with actual content.
Complete one file fully before moving to the next.

### Step 4 — Verify

```bash
python tmp/check_all_categories.py --category {{CODE}} --v3-only
```

All files in the batch should now show `v6.0 / complete`.
H1 count should be 1 per file.

### Step 5 - Commit

Commit in batches of **10 created/upgraded files** (non-negotiable):

```bash
git add technical-mastery/{{TIER}}/{{FOLDER}}/
git commit -m "upgrade: ->v6.0 {{CODE}}-{{START}}-{{CODE}}-{{END}} {{CATEGORY_NAME}} - batch {{BATCH_N}}"
```

**Batch Rules:**

- Do NOT commit after individual files - batch every 10 upgraded files
- Last batch exception: if fewer than 10 files remain after the last full batch, commit all remaining as the final commit
- Do NOT `git push`

This workflow ends after the commit step.

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

## Quality Constitution (Non-Negotiable)

Every upgraded entry MUST pass ALL eight quality tests.
Full spec: `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md` Section 7.

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

## Common mistakes to avoid

- Using unapproved tags (e.g. `replication`, `consistency`, `repair`)
- Em dashes (`—`) anywhere in the file — use hyphen (`-`)
- `parent:` value not matching index.md title exactly
- Missing blank line before/after `---` separators
- Section 5.15 included when there is no distinct lifecycle
- `depends_on` with keyword names instead of CODE-NNN IDs
- ASCII diagrams wider than 59 characters
- ASCII diagram without matching Mermaid block below (DUAL format required)
- `# H1` in body duplicating YAML `title` (Just the Docs renders title as H1)
- Consecutive bold-label lines without blank line between them
- Running PS1 scripts with `powershell` instead of `pwsh` (corrupts emoji)
- Using `[System.Text.Encoding]::UTF8` instead of `::new('utf-8')` (adds BOM)
