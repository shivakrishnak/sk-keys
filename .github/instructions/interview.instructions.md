---
applyTo: "interview/**"
description: "Rules for generating and editing Interview Mastery Dictionary v3.0 content - 19 sections, scaffold workflow, Q&A format"
---

# Interview Mastery Dictionary - Auto-Loaded Instructions

> These instructions auto-attach when editing files under `interview/`.
> Full generation spec: `interview/_config/INTERVIEW_PROMPT.md` (v3.0)

## Relationship to Main Dictionary

The `/dictionary/` and `/interview/` systems are **completely separate**:

- Do NOT apply `GENERATOR_PROMPT.md` rules to `/interview/` files
- Do NOT apply `INTERVIEW_PROMPT.md` rules to `/dictionary/` files
- Do NOT create files in `/dictionary/` when working on interview content

## Workspace Structure

```
interview/
  _config/
    INTERVIEW_PROMPT.md          # Master generation spec v3.0
    interview_scaffold.py        # Scaffold generator (Python 3.14)
    generate-content.ps1         # Batch content generation
    generate-keywords.ps1        # Keyword generation/scaffolding
    topic-registry.md            # Topic-to-folder mapping
    README.md                    # Generation guide
  index.md                       # Interview nav root
  java/                          # Topic folders
  java-concurrency/
  hibernate/
  spring/
  ...
```

## Prompts (in .github/prompts/)

| Prompt                    | Purpose                                 |
| ------------------------- | --------------------------------------- |
| `@interview-fill-content` | Fill [FILL:...] stubs with real content |
| `@interview-scaffold`     | Run scaffold generator for a topic      |

## Content Structure - 19 Sections per Keyword

1. Title (`# KEYWORD NAME`)
2. TL;DR (one sentence, 25 words max)
3. The Problem This Solves (World Without It / Breaking Point / Evolution)
4. Textbook Definition
5. Understand It in 30 Seconds (One line / One analogy / One insight)
6. First Principles (Invariants / Trade-offs / Essential vs Accidental)
7. Mental Model / Analogy (blockquote + mapping + breakdown)
8. Gradual Depth - Five Levels (Anyone / Junior / Mid / Senior / Distinguished + Senior-to-Staff Leap)
9. How It Works (summarized but complete mechanism)
10. Complete Picture - End-to-End Flow (normal + failure + scale)
11. Code Example (CONDITIONAL - BAD then GOOD, production-grade)
12. Quick Reference Card (11 fields + 3 things + interview one-liner)
13. Mastery Checklist (5 indicators: EXPLAIN/DEBUG/DECIDE/BUILD/EXTEND)
14. The Surprising Truth (one counterintuitive fact)
15. Comparison Table (CONDITIONAL - 2+ alternatives + Rapid Decision Tree)
16. Common Misconceptions (min 4 rows, danger-ordered)
17. Failure Modes and Diagnosis (min 3 modes with real diagnostic commands)
18. Interview Deep-Dive (CAPSTONE - scaled by difficulty)
19. Related Keywords (prerequisites / builds-on / alternatives)

## Interview Deep-Dive Rules (Critical)

- **Minimum scales by difficulty:** easy=7, medium=9, hard=12
- Every question MUST have a **complete, detailed answer** (200-500 words)
- **Tag each question** with: `[JUNIOR]` `[MID]` `[SENIOR]` `[STAFF]`
- **End every answer** with `*What separates good from great:*`
- **Add `*Likely follow-up:*`** after each `*Why they ask:*`
- **Include timing guidelines table** at section start
- **At least 1 DEBUGGING + 1 TRADE-OFF question per keyword** (mandatory)
- **At least 1 BEHAVIORAL question for medium/hard keywords**
- Must cover at least 5 of 9 question categories

## Formatting Rules

- Code lines: max 70 characters
- ASCII diagrams: max 59 characters wide
- Paragraphs: max 5 sentences
- BAD pattern before GOOD pattern in all code examples
- Every `###` heading preceded by `---` with blank lines
- Keywords within a file separated by double horizontal rules
- No em dashes anywhere - use regular hyphens only

## Encoding Rules

- UTF-8 without BOM
- Always use `pwsh` (PowerShell 7+), NEVER `powershell.exe`
- `[System.Text.UTF8Encoding]::new($false)` for file writing
- Python: `$env:USERPROFILE\.local\bin\python3.14.exe`
- No emojis in YAML frontmatter

## File Frontmatter Format

```yaml
---
title: Topic - Subtopic
topic: Topic
subtopic: Subtopic
keywords:
  - Keyword One
  - Keyword Two
difficulty_range: easy | medium | hard | mixed
status: draft | in-progress | complete
version: 3
---
```

## Scaffold Workflow

1. **Scaffold:** `& "$env:USERPROFILE\.local\bin\python3.14.exe" interview/_config/interview_scaffold.py <topic>`
2. **Fill content:** Use `@interview-fill-content` prompt or manually replace `[FILL:...]` stubs
3. **One keyword at a time:** Read scaffold block, replace with complete content, move to next

## Generation Workflows

**Existing topic:** `Generate interview mastery content: Topic: Java, File: Java - Collections.md`

**New topic:** `Create new interview mastery topic: Angular` (checks registry, generates keywords, creates files)

**From dictionary:** `Generate interview content from: tier-3-java` (scans dictionary, maps to interview topics)

## Folder/File Rules

- One folder per main topic (lowercase, hyphens)
- Each folder has `index.md` listing sub-topic files
- Sub-topic files: `{Topic} - {Subtopic}.md`
- Each file contains 5-20 related keywords
- Separator in filenames: SPACE-HYPHEN-SPACE (never em dash)

> For the complete 1050-line generation spec with all section rules, see `interview/_config/INTERVIEW_PROMPT.md`.
