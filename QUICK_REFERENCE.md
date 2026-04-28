# ⚡ Quick Reference: Adding New Markdown Files

**50-second workflow for adding markdown files to GitHub Pages**

---

## The 4-Step Process

### Step 1: Create File (10 seconds)
```powershell
# Create file with proper naming
New-Item -Path "docs\java\☕ 012 — Garbage Collection.md" -Value "# Your Content"
```

**Pattern:** `☕ NNN — Title Here.md`
- 🎯 Replace `☕` with section emoji
- 🎯 Replace `NNN` with 3-digit number (001, 002, 003...)
- 🎯 Replace `Title Here` with your page title

### Step 2: Add Content (variable)
Edit your markdown file and add content

### Step 3: Run Automation (20 seconds)
```powershell
.\Update-MarkdownFrontmatter.ps1
```

**What happens automatically:**
- ✅ Jekyll YAML frontmatter added
- ✅ Title extracted from filename
- ✅ Navigation order set to file number (012)
- ✅ Clean URL generated (`/java/garbage-collection/`)
- ✅ Parent relationship set

### Step 4: Push to GitHub (20 seconds)
```bash
git add docs/
git commit -m "Add Garbage Collection topic"
git push origin main
```

**Wait 1-2 minutes → File appears in GitHub Pages!**

---

## Emoji Reference

Copy-paste the correct emoji for your section:

| Section | Emoji | Example |
|---------|-------|---------|
| Java | ☕ | `☕ 012 — Topic.md` |
| Spring | 🌱 | `🌱 001 — Topic.md` |
| Distributed Systems | 🔗 | `🔗 001 — Topic.md` |
| Databases | 💾 | `💾 001 — Topic.md` |
| Messaging & Streaming | 📨 | `📨 001 — Topic.md` |
| Networking & HTTP | 🌐 | `🌐 001 — Topic.md` |
| OS & Systems | 🖥️ | `🖥️ 001 — Topic.md` |
| System Design | 🏗️ | `🏗️ 001 — Topic.md` |
| DSA | 🔧 | `🔧 001 — Topic.md` |
| Software Design | 🧩 | `🧩 001 — Topic.md` |
| Cloud & Infrastructure | ☁️ | `☁️ 001 — Topic.md` |
| DevOps & SDLC | 🔄 | `🔄 001 — Topic.md` |

---

## Parent Titles

You no longer need to pass parent titles manually.

```powershell
.\Update-MarkdownFrontmatter.ps1
```

The script now scans the entire `docs` tree recursively and computes:
- parent relationships
- `nav_order`
- `has_children`
- canonical permalinks

---

## Real Examples

### Adding 3 New Java Topics

```powershell
# 1. Create files
New-Item -Path "docs\java\☕ 012 — Garbage Collection.md" -Value "# Content"
New-Item -Path "docs\java\☕ 013 — Finalization.md" -Value "# Content"
New-Item -Path "docs\java\☕ 014 — Memory Leak Detection.md" -Value "# Content"

# 2. Run automation
.\Update-MarkdownFrontmatter.ps1

# 3. Push
git add docs/java/
git commit -m "Add 3 Java GC topics"
git push origin main

# Done! Files appear in GitHub Pages in 1-2 minutes
```

### Adding to Multiple Sections

```powershell
# Update all docs folders and files at once
.\Update-MarkdownFrontmatter.ps1

git add docs/
git commit -m "Update all documentation sections"
git push origin main
```

---

## Number Extraction

The automation script extracts numbers from filenames:

```
Input File Name              → nav_order
─────────────────────────────┼───���──────
☕ 001 — Title.md            → 1
☕ 012 — Title.md            → 12
🔗 001 — CAP Theorem.md      → 1
💾 042 — Indexing.md          → 42
```

**Important:** Use 3-digit numbers (001, 002, 003...) for proper extraction and ordering

---

## What Gets Generated

**Input:**
```
docs/java/☕ 012 — Garbage Collection.md
```

**Automatically Created Frontmatter:**
```yaml
---
layout: default
title: "Garbage Collection"
parent: "Java Fundamentals"
nav_order: 12
permalink: /java/garbage-collection/
---
```

**GitHub Pages URL:**
```
https://your-site.com/java/garbage-collection/
```

**Position in Navigation:**
- Section: Java Fundamentals
- Item #12 (between Stack Frame and Operand Stack)

---

## Mistakes to Avoid

❌ Single digit numbers: `☕ 1 — Topic.md`  
→ Use `☕ 001 — Topic.md` instead

❌ Wrong emoji: `🌱 001 — Topic.md` (Spring emoji in Java folder)  
→ Use `☕ 001 — Topic.md` for Java

❌ No title: `☕ 012.md`  
→ Use `☕ 012 — Your Title.md`

❌ Manual frontmatter: Typing YAML yourself  
→ Run the automation script instead

❌ Forgetting to commit: Running script but not pushing  
→ Always: create → automate → commit → push

---

## Common Commands

### Add Single File to Java
```powershell
.\Update-MarkdownFrontmatter.ps1
```

### Add to Spring
```powershell
.\Update-MarkdownFrontmatter.ps1
```

### Add to Distributed Systems
```powershell
.\Update-MarkdownFrontmatter.ps1
```

### Update All Sections
```powershell
.\Update-MarkdownFrontmatter.ps1
```

### Check What Will Be Processed
```powershell
Get-ChildItem "docs\java" -Filter "☕*.md" | 
    Where-Object { $_.Name -ne "index.md" }
```

---

## Success Example

```
✅ Created: ☕ 012 — Garbage Collection.md
✅ Ran: Update-MarkdownFrontmatter.ps1
   └─ Title extracted: "Garbage Collection"
   └─ Nav order set: 12
   └─ URL created: /java/garbage-collection/
   └─ Parent assigned: "Java Fundamentals"
✅ Committed: "Add Garbage Collection topic"
✅ Pushed: to main branch
✅ Waiting: 1-2 minutes for GitHub Pages build...
✅ Live: File appears under Java Fundamentals in navigation! 🎉
```

---

## Still Have Questions?

See detailed guide: `docs/MARKDOWN_AUTOMATION_GUIDE.md`

---

**Total Time: ~2 minutes per file** ⚡
**Manual YAML Work: Zero** ✨
**GitHub Pages Accessibility: 100%** 🚀


