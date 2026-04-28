# Markdown Template with Table of Contents

Use this as a template for ALL your new markdown files.

---

## Template: File with Table of Contents

```markdown
---
layout: default
title: "Your Page Title"
parent: "Parent Section Name"
nav_order: 1
permalink: /your-section/your-page/
---

# ☕ Your Main Title
{: .no_toc }

## Table of Contents
{:toc}

---

## Main Section 1

### Subsection 1.1
Content here...

### Subsection 1.2
Content here...

## Main Section 2

Content here...

### Subsection 2.1
Content here...

### Subsection 2.2
Content here...

## Main Section 3

Content here...

---
```

---

## Copy-Paste Ready Templates

### For Java Topics

```markdown
---
layout: default
title: "Your Topic"
parent: "Java Fundamentals"
nav_order: 12
permalink: /java/your-topic/
---

# ☕ Your Topic
{: .no_toc }

## Table of Contents
{:toc}

---

## Overview

## How It Works

## Key Concepts

## Examples

## Best Practices
```

### For Other Sections

```markdown
---
layout: default
title: "Your Topic"
parent: "Section Name"
nav_order: 1
permalink: /section/topic/
---

# 🔗 Your Topic
{: .no_toc }

## Table of Contents
{:toc}

---

## Introduction

## Core Concepts

## Implementation

## Advanced Topics

## Best Practices
```

---

## Key Requirements

Every TOC file needs:

✅ `{: .no_toc }` on main heading  
✅ `## Table of Contents` heading  
✅ `{:toc}` to generate the TOC  
✅ `---` separator after TOC  
✅ Proper heading hierarchy (# → ## → ###)

---

## What Each Part Does

| Part | Purpose | Example |
|------|---------|---------|
| `{: .no_toc }` | Hides main heading from TOC | `# My Title\n{: .no_toc }` |
| `## Table of Contents` | TOC section heading | Appears before the `{:toc}` |
| `{:toc}` | Generates TOC from headings | `{:toc}` |
| `---` | Visual separator | Line break after TOC |
| `##` headings | Included in TOC | Major sections |
| `###` headings | Included in TOC | Subsections |

---

## Common Mistakes (Don't Do These!)

❌ **Forgetting `{: .no_toc }`**
- Your main title will appear in the TOC twice

❌ **Skipping heading levels**
- Wrong: `# Title` → `### Subsection` (skip ##)
- Right: `# Title` → `## Section` → `### Subsection`

❌ **Placing `{:toc}` in wrong location**
- Wrong: In the middle of content
- Right: After `## Table of Contents` heading

❌ **Using too many heading levels**
- Limit to 3-4 levels deep for readability

---

## Emoji Emojis by Section

Use these in your file names and headings:

| Section | Emoji | Example |
|---------|-------|---------|
| Java | ☕ | `# ☕ Garbage Collection` |
| Spring | 🌱 | `# 🌱 Spring Boot` |
| Distributed | 🔗 | `# 🔗 Consensus` |
| Databases | 💾 | `# 💾 Indexing` |
| Messaging | 📨 | `# 📨 Kafka` |
| Networking | 🌐 | `# 🌐 DNS` |
| OS/Systems | 🖥️ | `# 🖥️ Processes` |
| System Design | 🏗️ | `# 🏗️ Load Balancing` |
| DSA | 🔧 | `# 🔧 Binary Trees` |
| Software Design | 🧩 | `# 🧩 Design Patterns` |
| Cloud | ☁️ | `# ☁️ Kubernetes` |
| DevOps | 🔄 | `# 🔄 CI/CD Pipeline` |

---

## How to Use This Template

1. Copy the template for your section type
2. Replace placeholders with your content
3. Keep the `{: .no_toc }`, `## Table of Contents`, and `{:toc}` lines
4. Add your section headings as `##` level
5. Add subsection headings as `###` level

---

## After Adding TOC

When deployed to GitHub Pages:
- ✅ TOC appears as clickable navigation
- ✅ Each link jumps to that section
- ✅ Works on desktop AND mobile
- ✅ Updates automatically from headings
- ✅ Search still works on all content

---

## Files Already Updated (Examples)

These files already have TOC - check them out:
- README.md
- STATUS.md
- QUICK_REFERENCE.md
- MARKDOWN_AUTOMATION_GUIDE.md
- index.md

---

## Next Steps

1. Pick a file you're creating/editing
2. Copy the appropriate template above
3. Fill in your content with proper heading levels
4. Keep the `{:toc}` section intact
5. Deploy to GitHub Pages
6. Click the TOC to verify it works!

---

**Ready to go!** Use this template for all your new markdown files.

