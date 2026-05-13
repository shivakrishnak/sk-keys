---
mode: agent
description: "Generate or fill interview keyword content using keyword-batch mode (1-3 keywords at a time)"
tools:
  - read_file
  - replace_string_in_file
  - multi_replace_string_in_file
  - run_in_terminal
  - file_search
  - grep_search
---

# Generate Interview Content (keyword-batch)

Generate complete v3.0 interview mastery content for the next unfilled
keywords in a file. Works with both new files (frontmatter only) and
files with existing `[FILL:]`/`[TODO:]` stubs.

## Voice

Precise like Josh Bloch. Clear like Martin Fowler. Intuitive like
Feynman. Production-scarred like a senior systems architect.
Interview-ready like a FAANG bar raiser.

## Core Rules (non-negotiable)

1. **Generate complete 19-section content** for each keyword
2. **BAD before GOOD** in all code examples
3. **Code lines max 70 chars**, ASCII diagrams max 59 chars wide
4. **Min 4 misconception rows**, min 3 failure modes per keyword
5. **Interview Q&A must have COMPLETE answers** (200-500 words each)
6. **No em dashes** anywhere - use hyphens only
7. **UTF-8 no BOM** - no special characters in YAML frontmatter

## Section-Specific Rules (condensed)

| Section             | Key Rule                                                                                        |
| ------------------- | ----------------------------------------------------------------------------------------------- |
| TL;DR               | Max 25 words. What + why. Zero jargon.                                                          |
| Problem             | WORLD WITHOUT IT -> BREAKING POINT -> INVENTION MOMENT -> EVOLUTION                             |
| 30 Seconds          | One line (15 words) + One analogy (blockquote) + One insight                                    |
| First Principles    | 3 invariants -> derived design -> gain/cost -> essential/accidental                             |
| Mental Model        | Blockquote analogy + bullet mapping + "breaks down" sentence                                    |
| Five Levels         | L1-L5 + Senior-to-Staff Leap (required for medium/hard)                                         |
| Code Example        | BAD then GOOD. Real-world, not toy. Include test/verify.                                        |
| Quick Reference     | 11 fields + 3 things to remember + interview one-liner                                          |
| Mastery Checklist   | 5 indicators: EXPLAIN/DEBUG/DECIDE/BUILD/EXTEND                                                 |
| Misconceptions      | Min 4 rows. Most dangerous first.                                                               |
| Failure Modes       | Min 3. Symptom/Root Cause/Diagnostic (real command)/Fix/Prevention                              |
| Interview Deep-Dive | Min 7 Qs for easy, 9 for medium, 12 for hard. Tags + full answers + "What separates good/great" |
| Related Keywords    | Prerequisites / Builds on this / Alternatives - 2-3 each                                        |

## Sizing (words per keyword)

| Concept Type                  | Target Words |
| ----------------------------- | ------------ |
| Tiny (single-purpose, atomic) | 600-1,000    |
| Medium (one mechanism)        | 1,200-2,500  |
| Foundational (multi-faceted)  | 3,000-5,000  |

## Workflow

1. Read the target file - extract `keywords:` and `difficulty_range:` from frontmatter
2. Detect which keywords are already complete (have real content, not stubs)
3. Pick next 1-3 unfilled keywords (1 for hard, 2-3 for easy/medium)
4. Generate complete 19-section content for each keyword in the batch
5. Write content to file (append or replace stubs)
6. Report: `Completed keyword N of M: [name]`
7. Auto-continue to next batch until all keywords complete
8. Verify: grep for `[TODO:` and `[FILL:` - must return zero

## Invocation

```
Generate content for: interview/java/Java - Basics.md
```

Or with specific keywords:

```
Generate content for: interview/java/Java - Basics.md
Keywords: Variables and Data Types, Operators and Control Flow
Difficulty: easy
```

Work through keywords in batch. Do NOT attempt all keywords in one pass.
