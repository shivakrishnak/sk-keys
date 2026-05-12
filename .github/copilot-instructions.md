# GitHub Copilot - Workspace Instructions

This workspace is the **sk-keys Technical Reference** containing two independent content systems:

1. **Technical Dictionary** (`dictionary/`) - 3,638+ keyword entries across 55 categories in 9 tiers, v4.0 spec
2. **Interview Mastery Dictionary** (`interview/`) - Interview-focused content with deep Q&A, v3.0 spec

These systems are **completely separate** - never mix their specs, rules, or output formats.

---

## Workspace Structure

```
Root (site essentials only)
  _config.yml                         Jekyll config
  Gemfile                             Jekyll dependencies
  index.md                            Site root page
  README.md                           Repo readme

dictionary/
  _config/                            Dictionary specs and scripts
    GENERATOR_PROMPT.md               Master generation spec v4.0
    KEYWORD_GENERATOR_PROMPT.md       Category keyword generator v4.0
    CATEGORY_GENERATOR_PROMPT.md      Single-category generator
    TECHNICAL_DICTIONARY.md           Master keyword list
    GENERATE_QUEUE.md                 Generation queue guide
  index.md                            Dictionary nav root
  tier-1-foundations/                  Content tiers (9 total)
  tier-2-networking-security/
  ...

interview/
  _config/                            Interview specs and scripts
    INTERVIEW_PROMPT.md               Master generation spec v3.0
    interview_scaffold.py             Scaffold generator
    generate-content.ps1              Batch content generation
    generate-keywords.ps1             Keyword scaffolding
    topic-registry.md                 Topic-to-folder mapping
  index.md                            Interview nav root
  java/                               Topic folders
  java-concurrency/
  hibernate/
  spring/
  ...

.github/
  agents/                             Custom Copilot agents
    dictionary.agent.md               /dictionary - generate/scale dict content
    interview.agent.md                /interview - generate/scale interview content
  instructions/                       Auto-attach instructions
    dictionary.instructions.md        Loads for dictionary/** edits
    interview.instructions.md         Loads for interview/** edits
  prompts/                            Copilot prompt files
    dict-generate-entries.prompt.md   Generate dictionary entries
    dict-generate-keywords.prompt.md  Generate dictionary keywords
    dict-upgrade-batch.prompt.md      Upgrade dictionary to v4.0
    interview-fill-content.prompt.md  Fill interview scaffolds
    interview-scaffold.prompt.md      Run scaffold generator
  workflows/pages.yml                 GitHub Pages deployment

tmp/                                  Historical/utility scripts
```

## How Instructions Load

| Context                       | What loads automatically                            |
| ----------------------------- | --------------------------------------------------- |
| Any interaction               | This file (lean overview + shared rules)            |
| Editing `dictionary/**` files | + `.github/instructions/dictionary.instructions.md` |
| Editing `interview/**` files  | + `.github/instructions/interview.instructions.md`  |
| Using `/dictionary` agent     | Agent instructions + reads specs on demand          |
| Using `/interview` agent      | Agent instructions + reads specs on demand          |
| Using `@dict-*` prompts       | Prompt-specific instructions + agent tools          |
| Using `@interview-*` prompts  | Prompt-specific instructions + agent tools          |

## Shared Rules (both systems)

### Encoding Safety

- Always use `pwsh` (PowerShell 7+), NEVER `powershell.exe`
- UTF-8 without BOM: `[System.Text.UTF8Encoding]::new($false)`
- Python path: `$env:USERPROFILE\.local\bin\python3.14.exe`

### Formatting

- No em dashes anywhere - use regular hyphens only
- Code lines: max 70 characters
- ASCII diagrams: max 59 characters wide
- BAD pattern before GOOD pattern in all code examples
- Every `###` heading preceded by `---` with blank lines

### YAML

- Double-quote any title value containing `: ` (colon + space)
- File MUST start at byte 0 with `---` (no BOM, no whitespace)

### Git Workflow

```bash
git add dictionary/ interview/
git commit -m "feat: <description>"
# Do NOT git push
```

## Quick Reference - Dictionary

| Item                | Location                                          |
| ------------------- | ------------------------------------------------- |
| Full spec           | `dictionary/_config/GENERATOR_PROMPT.md`          |
| Keyword generator   | `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md`  |
| Master keyword list | `dictionary/_config/TECHNICAL_DICTIONARY.md`      |
| Generation queue    | `dictionary/_config/GENERATE_QUEUE.md`            |
| Auto-instructions   | `.github/instructions/dictionary.instructions.md` |

**Version Registry:** `LATEST_VERSION` = 4, `LATEST_VERSION_LABEL` = v4.0, `STUB_VERSION` = 0

## Quick Reference - Interview

| Item               | Location                                         |
| ------------------ | ------------------------------------------------ |
| Full spec          | `interview/_config/INTERVIEW_PROMPT.md`          |
| Scaffold generator | `interview/_config/interview_scaffold.py`        |
| Topic registry     | `interview/_config/topic-registry.md`            |
| Content generator  | `interview/_config/generate-content.ps1`         |
| Auto-instructions  | `.github/instructions/interview.instructions.md` |

**Spec Version:** `SPEC_VERSION` = 3, `SPEC_LABEL` = v3.0

## Default Behaviour

- When asked to work on **dictionary** content: read `dictionary/_config/GENERATOR_PROMPT.md` for the full spec
- When asked to work on **interview** content: read `interview/_config/INTERVIEW_PROMPT.md` for the full spec
- When asked to generate/create/upgrade entries, apply all rules automatically without confirmation
- When editing dictionary files, the dictionary instructions auto-load with the Category Code Registry and section rules
- When editing interview files, the interview instructions auto-load with section structure and Q&A rules
