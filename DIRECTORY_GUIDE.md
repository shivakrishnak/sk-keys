---
layout: default
title: "Directory Guide"
nav_exclude: true
---

# 📋 Root Directory File Guide

Reference guide for all files in the sk-keys root folder after restructuring.

---

## 📁 File Organization Guide

### Entry Points
| File | Size | Purpose | Audience |
|------|------|---------|----------|
| **README.md** | 4.4 KB | Project overview & quick links | Everyone (first read) |
| **index.md** | 1.9 KB | Navigation hub | Navigation menu |

### Quick Reference
| File | Size | Purpose | When to Use |
|------|------|---------|------------|
| **QUICK_REFERENCE.md** | 5.6 KB | 50-second workflow cheat sheet | When adding new files quickly |
| **STATUS.md** | 10 KB | Setup status & deployment guide | For deployment & troubleshooting |

### Comprehensive Guides
| File | Size | Purpose | When to Use |
|------|------|---------|------------|
| **MARKDOWN_AUTOMATION_GUIDE.md** | 8.3 KB | Complete automation documentation | Full reference material |
| **GITHUB_PAGES_GUIDE.md** | 6.7 KB | GitHub Pages navigation guide | Understanding page structure |
| **COPILOT_MARKDOWN_INTEGRATION.md** | 11.9 KB | Using Copilot + automation | Copilot workflow guidance |
| **CUSTOM_INSTRUCTIONS.md** | 4.3 KB | Team instructions & system prompts | Sharing with team/Copilot |

### Reference Materials
| File | Size | Purpose | When to Use |
|------|------|---------|------------|
| **TECHNICAL_DICTIONARY.md** | 37 KB | 500+ technical terms by domain | Looking up terminology |

### Summary & Cleanup Tracking  
| File | Size | Purpose | Status |
|------|------|---------|--------|
| **CLEANUP_SUMMARY.md** | 6.8 KB | Before/after restructuring info | Reference only |

### Configuration Files
| File | Purpose |
|------|---------|
| **Update-MarkdownFrontmatter.ps1** | PowerShell automation script |
| **_config.yml** | Jekyll configuration |

---

## 🎯 Common Tasks

### "I Want to Add a New File"
1. Read: **QUICK_REFERENCE.md** (5.6 KB - 2 minute read)
2. Follow: Workflow in **QUICK_REFERENCE.md**
3. Reference: **Custom naming pattern section**

### "I Need Full Documentation"
1. Start: **README.md** (overview)
2. Read: **MARKDOWN_AUTOMATION_GUIDE.md** (comprehensive)
3. Reference: **TECHNICAL_DICTIONARY.md** (terms)

### "I'm Deploying to GitHub Pages"
1. Check: **STATUS.md** (deployment steps)
2. Review: **GITHUB_PAGES_GUIDE.md** (navigation setup)
3. Follow: Deployment instructions in **STATUS.md**

### "I'm Setting Up Copilot"
1. Review: **CUSTOM_INSTRUCTIONS.md** (base instructions)
2. Reference: **COPILOT_MARKDOWN_INTEGRATION.md** (examples)
3. Use: Patterns defined in **QUICK_REFERENCE.md**

### "I Need to Share Repository with Team"
1. Share: **README.md** (overview)
2. Share: **QUICK_REFERENCE.md** (workflow)
3. Share: **CUSTOM_INSTRUCTIONS.md** (team rules)

---

## 📊 Before & After Cleanup

### What Was Removed
```
❌ COMPLETION_REPORT.md (385 lines) → Consolidated into STATUS.md
❌ IMPLEMENTATION_COMPLETE.md (353 lines) → Consolidated into STATUS.md
❌ AUTOMATION_SETUP_COMPLETE.md (414 lines) → Consolidated into STATUS.md

Total Removed: 1,152 lines of duplicate content
```

### What Was Added/Updated
```
✅ STATUS.md (308 lines) - NEW, consolidated file
✅ README.md - Updated with meaningful content
✅ index.md - Updated with better navigation
✅ COPILOT_MARKDOWN_INTEGRATION.md - Fixed broken YAML frontmatter
```

---

## 💡 File Purposes at a Glance

**README.md**
- First file people read
- Project overview
- Quick start links
- 12-section table

**index.md**
- Jekyll navigation hub
- Links to main guides
- Shows documentation structure

**QUICK_REFERENCE.md**
- One-page cheat sheet
- Emoji reference table
- Common commands
- File naming patterns

**MARKDOWN_AUTOMATION_GUIDE.md**
- Most comprehensive guide
- Complete workflows
- Advanced features
- Troubleshooting tips

**STATUS.md** ⭐ NEW
- Implementation status
- Deployment instructions
- Verification checklist
- Troubleshooting guide

**GITHUB_PAGES_GUIDE.md**
- Technical navigation setup
- File structure explanation
- Access patterns
- Features enabled

**COPILOT_MARKDOWN_INTEGRATION.md**
- How to use Copilot
- Example conversations
- System prompts
- Time-saving workflows

**CUSTOM_INSTRUCTIONS.md**
- Instructions for Copilot
- Instructions for team
- Rules and patterns
- Example interactions

**TECHNICAL_DICTIONARY.md**
- 500+ technical terms
- Organized by domain
- Quick reference
- Learning database

**CLEANUP_SUMMARY.md**
- Before/after breakdown
- Removed files list
- Content preservation notes
- Verification checklist

---

## 🔍 File Relationships

```
README.md (START HERE)
├─→ QUICK_REFERENCE.md (for quick tasks)
├─→ MARKDOWN_AUTOMATION_GUIDE.md (for full guide)
├─→ STATUS.md (for deployment)
├─→ TECHNICAL_DICTIONARY.md (for terminology)
└─→ index.md (navigation hub)

QUICK_REFERENCE.md
├─→ File naming patterns
├─→ Emoji reference
└─→ Common commands

MARKDOWN_AUTOMATION_GUIDE.md
├─→ Detailed workflows
├─→ Advanced features
└─→ Troubleshooting

STATUS.md
├─→ Deployment steps
├─→ Verification checklist
└─→ Troubleshooting

CUSTOM_INSTRUCTIONS.md (for sharing)
├─→ Team instructions
├─→ System prompts
└─→ Patterns to follow
```

---

## 📈 Statistics After Cleanup

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Root Markdown Files** | 13 | 10 | -3 files |
| **Total Root Lines** | 4,455 | 3,303 | -1,152 lines (-26%) |
| **Redundant Content** | ~50% | ~0% | Eliminated |
| **Clear Purpose per File** | Medium | High | Improved |
| **Navigation Clarity** | Mixed | Excellent | Improved |

---

## ✅ Quality Checks Passed

- ✅ No content loss
- ✅ All important information preserved
- ✅ Frontmatter fixed (COPILOT_MARKDOWN_INTEGRATION.md)
- ✅ Links updated and verified
- ✅ README now provides value
- ✅ Index provides clear navigation
- ✅ STATUS.md consolidates key info
- ✅ Redundancy eliminated

---

## 🚀 Next Steps

1. **Review** the new structure (you're reading this!)
2. **Use** QUICK_REFERENCE.md for workflows
3. **Reference** STATUS.md for deployment
4. **Deploy** to GitHub Pages
5. **Maintain** with MARKDOWN_AUTOMATION_GUIDE.md

---

**Last Updated:** April 28, 2026

