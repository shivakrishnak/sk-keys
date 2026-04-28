---
layout: default
title: "Markdown Automation Guide"
nav_order: 18
permalink: /markdown-automation-guide/
---

# 🤖 Markdown Automation Guide

Complete guide to automatically generate Jekyll frontmatter for new markdown files without manual entry.

---

## 📋 Overview

Two PowerShell scripts are provided to automatically add Jekyll YAML frontmatter to your markdown files:

1. **`Update-MarkdownFrontmatter.ps1`** - Process a single section
2. **`Bulk-Update-All-Sections.ps1`** - Update all sections at once

---

## 🚀 Quick Start

### Adding New Files to Java Section

```bash
# 1. Create your markdown file with proper naming
New-Item -Path "docs/java/☕ 012 — Garbage Collection.md"

# 2. Run the update script
.\Update-MarkdownFrontmatter.ps1 -SectionPath "docs\java" -ParentTitle "Java Fundamentals"

# 3. File automatically gets Jekyll frontmatter!
```

### Result

Your file now has:
```yaml
---
layout: default
title: "Garbage Collection"
parent: "Java Fundamentals"
nav_order: 12
permalink: /java/garbage-collection/
---
```

---

## 📝 File Naming Convention

Follow this pattern for automatic number and title extraction:

### Format
```
☕ NNN — Title Here.md
```

### Examples
```
✅ ☕ 012 — Garbage Collection.md
✅ ☕ 013 — Finalization.md
✅ 🌱  001 — Dependency Injection.md
✅ 🔗  001 — CAP Theorem.md
✅ 💾  001 — ACID Properties.md
```

### How It Works
- **NNN** (3 digits) = Becomes `nav_order`
- **Title** = Extracted from filename (after emoji and number)
- **Emoji** = Preserved in permalinks as clean URL slug
- **.md** extension = Removed automatically

---

## 🛠️ Usage Examples

### Single Section Update

```powershell
# Update Java section
.\Update-MarkdownFrontmatter.ps1 `
    -SectionPath "docs\java" `
    -ParentTitle "Java Fundamentals"
```

**What it does:**
- Scans `docs/java/` for all `.md` files (except index.md)
- Extracts number and title from each filename
- Adds Jekyll YAML frontmatter
- Generates clean permalinks
- Sets sequential nav_order values

### Update Specific Section

```powershell
# Update Distributed Systems
.\Update-MarkdownFrontmatter.ps1 `
    -SectionPath "docs\Distributed Systems" `
    -ParentTitle "Distributed Systems"
```

### Bulk Update All Sections

```powershell
# Update all sections at once
.\Bulk-Update-All-Sections.ps1
```

**Processes:**
- Java Fundamentals
- Spring
- Distributed Systems
- Databases
- Messaging & Streaming
- Networking & HTTP
- OS & Systems
- System Design
- DSA
- Software Design
- Cloud & Infrastructure
- DevOps & SDLC

---

## 📊 What Gets Generated

### Input File
```
docs/java/☕ 012 — Garbage Collection.md
```

### After Running Script
```yaml
---
layout: default
title: "Garbage Collection"
parent: "Java Fundamentals"
nav_order: 12
permalink: /java/garbage-collection/
---

# Original content here...
(Your file content remains unchanged)
```

### As It Appears in GitHub Pages
- **URL:** `https://your-site.com/java/garbage-collection/`
- **Position:** Listed under Java Fundamentals, item #12
- **Title:** "Garbage Collection" in navigation menu

---

## 🔄 Workflow Example: Adding 5 New Java Topics

### Step 1: Create Files with Proper Names
```powershell
# Create files (manually or with script)
New-Item -Path "docs/java/☕ 012 — Garbage Collection.md" -Value "# Your content here"
New-Item -Path "docs/java/☕ 013 — Finalization.md" -Value "# Your content here"
New-Item -Path "docs/java/☕ 014 — Reference Queue.md" -Value "# Your content here"
New-Item -Path "docs/java/☕ 015 — Memory Leak Detection.md" -Value "# Your content here"
New-Item -Path "docs/java/☕ 016 — GC Tuning.md" -Value "# Your content here"
```

### Step 2: Run Automation Script
```powershell
.\Update-MarkdownFrontmatter.ps1 `
    -SectionPath "docs\java" `
    -ParentTitle "Java Fundamentals"
```

### Step 3: Verify Output
```powershell
Get-Content "docs/java/☕ 012 — Garbage Collection.md" -Head 20
# Shows YAML frontmatter added automatically!
```

### Step 4: Commit and Push
```bash
git add docs/java/
git commit -m "Add 5 new Java topics - Garbage Collection & Memory Management"
git push origin main
```

### Step 5: Verify in GitHub Pages
- Wait 1-2 minutes for build
- Check: All 5 new topics appear in Java Fundamentals section
- Verify: Numbered 12-16 in display order

---

## ✨ Features

### Automatic Extraction
- ✅ Extracts numbers from filename → `nav_order`
- ✅ Extracts title from filename → Page title
- ✅ Handles emoji prefixes (☕, 🌱, 🔗, etc.)
- ✅ Creates clean URL slugs

### Smart Updates
- ✅ Detects existing frontmatter
- ✅ Removes old frontmatter before adding new
- ✅ Preserves all original content
- ✅ Works with all UTF-8 characters

### Error Handling
- ✅ Validates section path exists
- ✅ Skips index.md files
- ✅ Reports errors per file
- ✅ Continues on individual file errors

---

## 🎯 Supported Sections

All 12 documentation sections are configured:

| Section | Path | Parent Title |
|---------|------|--------------|
| Java | `docs\java` | Java Fundamentals |
| Spring | `docs\spring` | Spring |
| Distributed Systems | `docs\Distributed Systems` | Distributed Systems |
| Databases | `docs\Databases` | Databases |
| Messaging & Streaming | `docs\Messaging & Streaming` | Messaging & Streaming |
| Networking & HTTP | `docs\Networking & HTTP` | Networking & HTTP |
| OS & Systems | `docs\OS & Systems` | OS & Systems |
| System Design | `docs\System Design` | System Design |
| DSA | `docs\DSA` | DSA |
| Software Design | `docs\Software Design` | Software Design |
| Cloud & Infrastructure | `docs\Cloud & Infrastructure` | Cloud & Infrastructure |
| DevOps & SDLC | `docs\DevOps & SDLC` | DevOps & SDLC |

---

## 📋 Troubleshooting

### Issue: "File already has frontmatter"
**Solution:** Script automatically detects and removes old frontmatter before adding new. No action needed.

### Issue: "Title not extracted correctly"
**Solution:** Check filename format. Use standard pattern:
```
☕ NNN — Title Here.md
```

### Issue: "Nav order is wrong"
**Solution:** Ensure filenames have 3-digit numbers:
- ✅ `☕ 001 — JVM.md` (correct)
- ❌ `☕ 1 — JVM.md` (wrong - needs 001)

### Issue: "Permalink has wrong characters"
**Solution:** Special characters in title are converted to hyphens. This is expected.
- Input: `Data I/O & Caching`
- Output URL: `/java/data-io-caching/`

---

## 🔧 Custom Arguments

The script supports custom arguments:

```powershell
# Use custom base permalink
.\Update-MarkdownFrontmatter.ps1 `
    -SectionPath "docs\java" `
    -ParentTitle "Java Fundamentals" `
    -BasePermalink "java-internals"  # Custom instead of auto-generated
```

---

## 📚 Complete Workflow

### For Teams/Continuous Updates

```powershell
# 1. Create content files with proper naming
# 2. Run bulk update
.\Bulk-Update-All-Sections.ps1

# 3. Review changes
git diff docs/

# 4. Commit
git add docs/
git commit -m "Add new content - auto-frontmatter generated"

# 5. Push
git push origin main

# 6. GitHub Pages automatically rebuilds (1-2 minutes)
# 7. New pages appear in navigation!
```

---

## 🚀 Advanced: Custom Section

To add automation for a new section:

```powershell
# Edit Bulk-Update-All-Sections.ps1
# Add to $sections array:

@{ Path = "docs\My New Section"; Parent = "My New Section" }

# Then run:
.\Bulk-Update-All-Sections.ps1
```

---

## ✅ Best Practices

1. **Use Standard Naming Convention**
   - Always use 3-digit numbers: 001, 002, 003...
   - Always include title after emoji and number
   - Example: `☕ 001 — Your Title Here.md`

2. **Test Locally First**
   - Run script on single section first
   - Verify GitHub Pages locally (if jekyll installed)
   - Then run on other sections

3. **Commit Regularly**
   ```bash
   git add docs/
   git commit -m "Add [section name] topics [number range]"
   git push
   ```

4. **Monitor Build**
   - Check GitHub Actions after push
   - Verify pages appear in navigation
   - Check clean URLs work

---

## 📞 Support

### Common Tasks

**Add 10 new Java topics:**
```powershell
# 1. Create files 012-021
# 2. Run script
.\Update-MarkdownFrontmatter.ps1 -SectionPath "docs\java" -ParentTitle "Java Fundamentals"
# 3. Done!
```

**Update entire docs folder:**
```powershell
.\Bulk-Update-All-Sections.ps1
```

**Check what will be generated (preview):**
```powershell
Get-ChildItem "docs\java" -Filter "*.md" | 
    Where-Object { $_.Name -ne "index.md" } |
    Select-Object Name
```

---

## 🎉 Result

No more manual YAML frontmatter! Just:
1. Create file with proper name
2. Run script
3. File appears in GitHub Pages automatically!

**Total time per file: < 1 second** ⚡

---

**Last Updated:** April 28, 2026


