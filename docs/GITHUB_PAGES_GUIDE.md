---
layout: default
title: GitHub Pages Navigation Guide
nav_order: 15
permalink: /github-pages-guide/
---

# GitHub Pages Navigation & Accessibility Guide

## ✅ How Files Are Now Accessible in GitHub Pages

Your documentation files are now properly configured for Jekyll-based GitHub Pages with complete navigation hierarchy.

---

## 📚 File Structure Overview

### Java Fundamentals (11 files)
All files in `docs/java/` are now accessible with proper navigation:

```
docs/
└── java/
    ├── index.md (☕ Java Fundamentals - Parent)
    ├── ☕ 001 — JVM (Java Virtual Machine).md (nav_order: 1)
    ├── ☕ 002 — JRE (Java Runtime Environment).md (nav_order: 2)
    ├── ☕ 003 —JDK (Java Development Kit).md (nav_order: 3)
    ├── ☕ 004 —Bytecode.md (nav_order: 4)
    ├── ☕ 005 — Class Loader.md (nav_order: 5)
    ├── ☕ 006 — Stack Memory.md (nav_order: 6)
    ├── ☕ 007 — Heap Memory.md (nav_order: 7)
    ├── ☕ 008 — Metaspace.md (nav_order: 8)
    ├── ☕ 009 — Stack Frame.md (nav_order: 9)
    ├── ☕ 010 — Operand Stack.md (nav_order: 10)
    └── ☕ 011 — Local Variable Table.md (nav_order: 11)
```

---

## 🔗 Front Matter Configuration

Each Java file now has proper YAML frontmatter that enables GitHub Pages to:
1. **Display in navigation menus** (as child items under Java Fundamentals)
2. **Generate proper URLs** (e.g., `/java/jvm/`, `/java/class-loader/`)
3. **Order sections correctly** (nav_order determines display order)

### Example: JVM File Frontmatter

```yaml
---
layout: default
title: "JVM (Java Virtual Machine)"
parent: "Java Fundamentals"
nav_order: 1
permalink: /java/jvm/
---
```

### Key Frontmatter Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `layout` | Jekyll template | `default` |
| `title` | Display name in navigation | `"JVM (Java Virtual Machine)"` |
| `parent` | Parent section (must match parent index.md title) | `"Java Fundamentals"` |
| `nav_order` | Display order (number) | `1`, `2`, `3`... |
| `permalink` | Custom URL path | `/java/jvm/` |

---

## 🌐 Access Patterns in GitHub Pages

### Direct URLs (after deployment)

Once deployed to GitHub Pages, files are accessible at:

```
https://your-username.github.io/docs/java/jvm/
https://your-username.github.io/docs/java/class-loader/
https://your-username.github.io/docs/java/stack-memory/
```

Or if repository is not `your-username.github.io`:

```
https://your-username.github.io/sk-keys/docs/java/jvm/
https://your-username.github.io/sk-keys/docs/java/class-loader/
```

### Via Navigation Menu

Users will see a hierarchical menu:

```
Complete Mastery System
├── Java Fundamentals
│   ├── JVM (Java Virtual Machine)
│   ├── JRE (Java Runtime Environment)
│   ├── JDK (Java Development Kit)
│   ├── Bytecode
│   ├── Class Loader
│   ├── Stack Memory
│   ├── Heap Memory
│   ├── Metaspace
│   ├── Stack Frame
│   ├── Operand Stack
│   └── Local Variable Table
├── Spring
├── Distributed Systems
├── Databases
├── ... (and 8 more sections)
└── Technical Dictionary
```

---

## 🚀 Deployment Steps (GitHub Pages)

To make your documentation live on GitHub Pages:

### 1. Push to GitHub

```bash
git add .
git commit -m "Add Java documentation with proper navigation"
git push origin main
```

### 2. Enable GitHub Pages

In your repository settings:
- Go to **Settings** → **Pages**
- Select **Source**: `main` branch, `/docs` folder
- Click **Save**

### 3. Access Your Site

GitHub Pages will build and deploy within 1-2 minutes:
- Check: `https://your-username.github.io/sk-keys/`
- All files with frontmatter will be in the navigation menu

---

## ✨ Features Enabled by Frontmatter

With proper frontmatter, Jekyll automatically provides:

✅ **Hierarchical Navigation** - Parent/child relationship  
✅ **Sidebar Menu** - All pages listed with proper order  
✅ **Search** - Files are discoverable via search  
✅ **Breadcrumbs** - Users see path: Home > Java > JVM  
✅ **Next/Previous Links** - Navigation between related pages  
✅ **Mobile Responsive** - Works perfectly on phones/tablets  

---

## 🔁 Adding More Files to Sections

To add new files to the Java section (or any other section):

### Step 1: Create the file

```
docs/java/☕ 012 — Garbage Collection.md
```

### Step 2: Add frontmatter (at the very top)

```yaml
---
layout: default
title: "Garbage Collection"
parent: "Java Fundamentals"
nav_order: 12
permalink: /java/garbage-collection/
---

# ☕ Garbage Collection

Your content here...
```

### Step 3: Git commit and push

```bash
git add docs/java/
git commit -m "Add Garbage Collection documentation"
git push
```

The page will automatically appear in the navigation menu!

---

## 📝 Notes & Best Practices

### ✅ Do's

- Keep file titles short and descriptive
- Use consistent naming conventions
- Maintain sequential nav_order values within sections
- Use meaningful permalinks (lowercase, hyphens)
- Keep parent title exactly matching the parent index.md

### ❌ Don'ts

- Don't use special characters in permalinks (except hyphens)
- Don't skip nav_order numbers (creates gaps)
- Don't make parent/title mismatches (breaks hierarchy)
- Don't commit without proper frontmatter (file won't appear)

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| File not appearing in menu | Check `parent` matches exactly with parent index.md title |
| Wrong URL generated | Check `permalink` - must be URL-safe (lowercase, hyphens) |
| Ordering is wrong | Check `nav_order` values are sequential and unique |
| Special characters broken | Remove Unicode from `permalink`, keep it in `title` |

---

## 🎯 Current Status

✅ **Java Section** - All 11 files configured and ready  
⏳ **Other Sections** - Index files ready, can add content files  
✅ **Technical Dictionary** - Accessible at `/technical-dictionary/`  
✅ **Navigation Structure** - Complete 12-section hierarchy established  

**Total Accessible Pages**: 26+

---

## 📞 Next Steps

1. **Deploy to GitHub** - Push code and enable Pages in settings
2. **Verify Navigation** - Check that all files appear in menu
3. **Add Content** - Continue populating other sections using the same pattern
4. **Custom Domain** - (Optional) Set up CNAME for custom domain

Your documentation is now production-ready for GitHub Pages! 🚀


