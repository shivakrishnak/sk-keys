# Interview Mastery Dictionary - Copilot Instructions

This workspace folder (`/interview/`) is the **Interview Mastery Dictionary** - a condensed, interview-focused technical reference with deep Q&A for every concept.

## Relationship to Main Dictionary

The main `/dictionary/` folder contains the full 24-section v4.0 Technical Dictionary entries. This `/interview/` system is **completely separate** - different prompt, different structure, different purpose. Never mix the two systems:

- Do NOT apply `GENERATOR_PROMPT.md` rules to `/interview/` files
- Do NOT apply `INTERVIEW_PROMPT.md` rules to `/dictionary/` files
- Do NOT create files in `/dictionary/` when working on interview content
- Do NOT modify `/dictionary/` files when working on interview content

## Default Behaviour

When asked to generate, create, or edit any file under `/interview/`, apply all rules from `interview/config/INTERVIEW_PROMPT.md` automatically. Do not ask for confirmation before generating.

## Prompt Files

| Prompt                                        | Purpose                                                  |
| --------------------------------------------- | -------------------------------------------------------- |
| `interview/config/INTERVIEW_PROMPT.md`        | Master generation prompt for interview mastery entries   |
| `interview/config/generate-content.ps1`       | Batch content generation script                          |
| `interview/config/generate-keywords.ps1`      | Keyword generation and folder/file scaffolding           |
| `interview/config/topic-registry.md`          | Topic-to-folder mapping and dictionary category mappings |
| `KEYWORD_GENERATOR_PROMPT.md`                 | Master keyword generation spec (v3.0)                      |
| `.github/prompts/generate-keywords.prompt.md` | Prompt for category/tier keyword processing              |

## Design Considerations

When working with interview content, follow these rules for different scenarios:

1. **New topic (no folder/index.md exists):** Use `KEYWORD_GENERATOR_PROMPT.md` (v3.0) to generate a comprehensive keyword list. Analyse where the topic belongs in the tier structure (tier-1 through tier-9). Create the folder, index.md, and sub-topic files. Apply folder/file rules. Generate content using `INTERVIEW_PROMPT.md`.

2. **Brand-new topic (e.g., Angular, not in dictionary):** Analyse which tier/category the topic belongs to. Use `KEYWORD_GENERATOR_PROMPT.md` to generate keywords covering L0 through L5+META levels. Create the relevant folders and files. Apply all folder/file rules. Generate content.

3. **New subtopic for existing topic (e.g., React Hooks):** Analyse where the subtopic fits within the existing topic structure. Create the file in the existing topic folder. Use `KEYWORD_GENERATOR_PROMPT.md` to generate a focused keyword list for the subtopic. Apply file rules. Generate content.

4. **Existing dictionary category (e.g., JVM, JCC):** Scan the dictionary `index.md` and analyse keywords. Check for new folder/file opportunities (gaps, missing subtopics). Apply folder/file rules. Generate content for uncovered keywords.

## Folder Structure Rules

- One folder per main technology/skill/topic (lowercase, hyphens for multi-word)
- Each folder contains an `index.md` listing all sub-topic files
- Sub-topic files use format: `{Topic} - {Subtopic}.md`
- Each sub-topic file contains 5-20 related keywords
- Separator in filenames: space + HYPHEN + space (NEVER em dash)

## Content Rules Summary

Each keyword within a file has 19 sections (see `INTERVIEW_PROMPT.md` v3.0 for full spec):

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
11. Code Example (CONDITIONAL - real-world, BAD then GOOD, production-grade)
12. Quick Reference Card (11 fields incl KEY NUMBERS, TRIGGER PHRASE, OPENING SENTENCE + 3 things + interview one-liner)
13. Mastery Checklist (5 indicators: EXPLAIN/DEBUG/DECIDE/BUILD/EXTEND)
14. The Surprising Truth (one counterintuitive fact)
15. Comparison Table (CONDITIONAL - when 2+ alternatives exist + Rapid Decision Tree)
16. Common Misconceptions (min 4 rows, danger-ordered)
17. Failure Modes and Diagnosis (min 3 modes with real diagnostic commands)
18. Interview Deep-Dive (CAPSTONE - scaled by difficulty: easy=7, medium=9, hard=12 + timing + likely follow-ups)
19. Related Keywords (prerequisites / builds-on / alternatives)

## Interview Deep-Dive Rules (Critical)

This is the most important section. Rules:

- **No cap on question count** - more is better
- **Minimum scales by difficulty:** easy=7, medium=9, hard=12
- Every question MUST have a **complete, detailed answer** (not bullet hints)
- **Tag each question** with difficulty: `[JUNIOR]` `[MID]` `[SENIOR]` `[STAFF]`
- **End every answer** with `*What separates good from great:*` insight line
- **Add `*Likely follow-up:*`** after each question's `*Why they ask:*` line
- **Include timing guidelines table** at the start of each Interview Deep-Dive
- Answers should demonstrate natural depth ("low-key impress the interviewer")
- Answers can be long but must have clear structure and learning progression
- **Must cover at least 5 of 9 question categories** per keyword
- Required question types: conceptual, debugging, architecture, trade-off, production, hands-on, system design, comparison, **behavioral**
- **At least 1 DEBUGGING + 1 TRADE-OFF question per keyword** (mandatory)
- **At least 1 BEHAVIORAL question for medium/hard keywords** (mandatory)
- Questions must be scenario-based, practical, and test real experience
- No duplicate questions across keywords in the same file

## Encoding Rules

- All files: UTF-8 without BOM
- PowerShell scripts: always use `pwsh` (PowerShell 7+), never `powershell.exe`
- File writing: `[System.Text.UTF8Encoding]::new($false)` (no BOM)
- No emojis in YAML frontmatter (encoding safety)
- Section headers in content body MUST use emoji prefixes as defined in spec
- No em dashes anywhere - use regular hyphens only

## Formatting Rules

- Code lines: max 70 characters
- ASCII diagrams: max 59 characters wide
- Paragraphs: max 5 sentences
- BAD pattern before GOOD pattern in all code examples
- Every `###` heading preceded by `---` with blank lines
- Keywords within a file separated by double horizontal rules (`---` then `---`)

## Generation Workflow

### Generate content for an existing topic

```
Generate interview mastery content:
  Topic: Java
  File: Java - Collections.md
```

### Generate a new topic from scratch

```
Create new interview mastery topic: Angular
```

This will:

1. Check `topic-registry.md` for existing mappings
2. Check if dictionary has a matching category (e.g., ANG)
3. Generate keyword list using `KEYWORD_GENERATOR_PROMPT.md` v3.0 spec
   (via `.github/prompts/generate-keywords.prompt.md`)
4. Analyse where the topic belongs (tier/category placement)
5. Create folder + index.md + content files

### Add a new subtopic to an existing topic

```
Add subtopic: React - Hooks
```

This will:

1. Verify the parent topic folder exists
2. Generate keywords using `KEYWORD_GENERATOR_PROMPT.md` v3.0
3. Create the subtopic file with YAML frontmatter
4. Generate content using `INTERVIEW_PROMPT.md`
5. Update the topic `index.md`

### Generate from existing dictionary tier or category

```
Generate interview content from: tier-3-java
Generate interview content from: JVM
```

This will:

1. Scan dictionary `index.md` for the category/tier
2. Analyse keywords for new folder/file opportunities
3. Map categories to interview topics via `topic-registry.md`
4. Create missing folders, stubs, and index files
5. Generate content for uncovered keywords

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
version: 2
---
```

Version field: `2` for v2.0 content (18 sections), `1` for legacy v1.0 content (14 sections), `0` for stubs.

No emojis. No Unicode stars. No special characters. Plain text only in YAML.
