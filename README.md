# sk-keys Technical Reference

A comprehensive software engineering reference with two content systems:

1. **Technical Mastery** - 3,638+ keyword entries across 55 categories in 9 tiers (v4.0)
2. **Interview Mastery Dictionary** - Interview-focused content with deep Q&A (v3.0)

## Structure

| Folder                | Purpose                                       |
| --------------------- | --------------------------------------------- |
| `technical-mastery/`         | technical-mastery entries organized by tier/category |
| `technical-mastery/_config/` | technical-mastery specs and generation scripts       |
| `interview/`          | Interview mastery entries organized by topic  |
| `interview/_config/`  | Interview specs and generation scripts        |
| `.github/`            | Copilot instructions, prompts, and workflows  |
| `tmp/`                | Historical utility scripts                    |

## Agents (recommended)

Use `/technical-mastery` or `/interview` in VS Code Copilot chat for end-to-end content generation:

```
/technical-mastery tier-3 JVM              Generate entries for JVM category
/technical-mastery upgrade tier-1 CSF      Upgrade CSF entries to v4.0
/technical-mastery new: PostgreSQL, Trino  Generate keywords + content for new topics
/technical-mastery "Strong SQL skills..."  Analyze description, create keywords + content

/interview Angular                  Create new interview topic with full content
/interview React hooks              Add subtopic to existing React topic
/interview from tier-3 JCC          Generate interview content from dictionary
/interview "Experience with AWS.." Analyze JD, create matching interview content
```

## Prompts

```bash
# Technical Mastery: @technical-mastery-generate-entries, @technical-mastery-generate-keywords, @technical-mastery-upgrade-batch
# Interview: @interview-fill-content, @interview-scaffold
```

## Specs

- Technical Mastery: `technical-mastery/_config/ENTRY_GENERATOR_PROMPT.md` (v4.0)
- Interview: `interview/_config/INTERVIEW_PROMPT.md` (v3.0)
- Keywords: `technical-mastery/_config/MASTERY_OS_PROMPT.md` (shared)

See `.github/copilot-instructions.md` for workspace instructions.

## Deploy to GitHub Pages

1. Go to **Settings -> Pages**
2. Select `main` branch, root `/`
3. Live at `https://shivakrishnak.github.io/sk-keys/`
