# sk-keys Technical Reference

A comprehensive software engineering reference with two content systems:

1. **Technical Dictionary** - 3,638+ keyword entries across 55 categories in 9 tiers (v4.0)
2. **Interview Mastery Dictionary** - Interview-focused content with deep Q&A (v3.0)

## Structure

| Folder                | Purpose                                       |
| --------------------- | --------------------------------------------- |
| `dictionary/`         | Dictionary entries organized by tier/category |
| `dictionary/_config/` | Dictionary specs and generation scripts       |
| `interview/`          | Interview mastery entries organized by topic  |
| `interview/_config/`  | Interview specs and generation scripts        |
| `.github/`            | Copilot instructions, prompts, and workflows  |
| `tmp/`                | Historical utility scripts                    |

## Agents (recommended)

Use `/dictionary` or `/interview` in VS Code Copilot chat for end-to-end content generation:

```
/dictionary tier-3 JVM              Generate entries for JVM category
/dictionary upgrade tier-1 CSF      Upgrade CSF entries to v4.0
/dictionary new: PostgreSQL, Trino  Generate keywords + content for new topics
/dictionary "Strong SQL skills..."  Analyze description, create keywords + content

/interview Angular                  Create new interview topic with full content
/interview React hooks              Add subtopic to existing React topic
/interview from tier-3 JCC          Generate interview content from dictionary
/interview "Experience with AWS.." Analyze JD, create matching interview content
```

## Prompts

```bash
# Dictionary: @dict-generate-entries, @dict-generate-keywords, @dict-upgrade-batch
# Interview: @interview-fill-content, @interview-scaffold
```

## Specs

- Dictionary: `dictionary/_config/GENERATOR_PROMPT.md` (v4.0)
- Interview: `interview/_config/INTERVIEW_PROMPT.md` (v3.0)
- Keywords: `dictionary/_config/KEYWORD_GENERATOR_PROMPT.md` (shared)

See `.github/copilot-instructions.md` for workspace instructions.

## Deploy to GitHub Pages

1. Go to **Settings -> Pages**
2. Select `main` branch, root `/`
3. Live at `https://shivakrishnak.github.io/sk-keys/`
