# Interview Mastery Dictionary - Instructions Redirect

> **Auto-loaded instructions:** `.github/instructions/interview.instructions.md`
> (automatically attached when editing any `interview/**` file)

This file is kept as a reference pointer. The authoritative instructions
live in `.github/instructions/interview.instructions.md` and auto-load
in VS Code Copilot when you edit interview content files.

## Quick Links

| Resource                                           | Purpose                                 |
| -------------------------------------------------- | --------------------------------------- |
| `.github/instructions/interview.instructions.md`   | Auto-loaded rules (19 sections, format) |
| `interview/_config/INTERVIEW_PROMPT.md`            | Full generation spec v3.0 (1050 lines)  |
| `interview/_config/interview_scaffold.py`          | Scaffold generator (Python 3.14)        |
| `interview/_config/topic-registry.md`              | Topic-to-folder mapping                 |
| `.github/prompts/interview-fill-content.prompt.md` | Fill [FILL:...] stubs with content      |
| `.github/prompts/interview-scaffold.prompt.md`     | Run scaffold generator                  |

## Workflow Summary

1. **Scaffold:** `@interview-scaffold` or run `interview_scaffold.py <topic>`
2. **Fill:** `@interview-fill-content` - replace [FILL:...] stubs keyword by keyword
3. **Verify:** Check all stubs replaced, validate section structure

## Design Considerations

| Scenario                      | Steps                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------ |
| New topic (no folder)         | Use `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md` v4.0 -> scaffold -> fill              |
| Brand-new topic (not in dict) | Analyse tier placement -> generate keywords -> scaffold -> fill                            |
| New subtopic (topic exists)   | Create file in existing folder -> `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md` -> fill |
| From dictionary category      | Scan dictionary index.md -> map via topic-registry.md -> scaffold -> fill                  |
