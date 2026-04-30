# 📚 Technical Dictionary

A software engineering dictionary — **1,770 keywords** across **43 categories** from CS fundamentals to AI & LLMs.

## Files

| File | Purpose |
|---|---|
| `GENERATOR_PROMPT.md` | Master prompt for generating dictionary entries |
| `TECHNICAL_DICTIONARY.md` | Complete master keyword list (001–1770) |
| `Update-MarkdownFrontmatter.ps1` | Recursively adds/updates GitHub Pages navigation frontmatter |
| `_config.yml` | Jekyll / GitHub Pages configuration |
| `docs/` | All dictionary entries, organized by category |

## Add a New Entry

```powershell
# 1. Create file following the naming convention
#    docs/<Category>/NNN — Keyword Name.md

# 2. Update navigation frontmatter
.\Update-MarkdownFrontmatter.ps1

# 3. Push
git add docs/
git commit -m "Add NNN — Keyword Name"
git push origin main
```

See `GENERATOR_PROMPT.md` for the full entry format specification.

## Deploy to GitHub Pages

1. Go to **Settings → Pages**
2. Select `main` branch, root `/` (not `/docs`)
3. Save — live at `https://shivakrishnak.github.io/sk-keys/`
