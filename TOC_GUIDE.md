# 📖 How to Add Table of Contents to Markdown Files

Complete guide to adding automatic table of contents to your Jekyll/GitHub Pages markdown files.

---

## Method 1: Automatic TOC with `{:toc}` (Recommended)

This is the easiest way. Jekyll automatically generates a clickable table of contents from your headings.

### Step 1: Add TOC Marker
At the top of your markdown file, after the frontmatter, add:

```markdown
---
layout: default
title: "Your Page Title"
parent: "Parent Section"
nav_order: 1
permalink: /your-page/
---

# Your Page Title
{: .no_toc }

## Table of Contents
{:toc}

---

## Section 1
Content here...

### Subsection 1.1
Content here...

## Section 2
Content here...
```

**Key points:**
- `{:toc}` generates the table of contents
- `{: .no_toc }` prevents the heading from appearing in the TOC
- Place the TOC marker after your main heading

---

## Method 2: Exclude Specific Headings from TOC

If you want some headings to NOT appear in the TOC:

```markdown
# Main Title
{: .no_toc }

## Table of Contents
{:toc}

---

## This will appear in TOC

### This subsection will appear

## This will also appear
{: .no_toc }

### This subsection will NOT appear
```

---

## Method 3: Custom Heading IDs (for better URLs)

Add custom IDs to headings for cleaner URLs in the TOC:

```markdown
## Heading with ID
{: #custom-id }
```

The TOC will link to `#custom-id` instead of auto-generated anchors.

---

## Complete Example

```markdown
---
layout: default
title: "Java Fundamentals"
parent: "Complete Mastery System"
nav_order: 1
permalink: /java/
---

# ☕ Java Fundamentals
{: .no_toc }

## Table of Contents
{:toc}

---

## JVM Concepts
{: #jvm-concepts }

Content about the Java Virtual Machine...

### Memory Model
Content about memory...

### Class Loading
Content about class loading...

## Runtime Environment

Content about the runtime...

### Bytecode Execution
Content about bytecode...

## Development Kit

Information about the JDK...

---

## Advanced Topics

More detailed content...
```

---

## Best Practices

### ✅ DO:
- Place `{:toc}` after your main heading
- Use `{: .no_toc }` on your page title
- Keep heading hierarchy logical (# → ## → ###)
- Use meaningful heading text
- Add `---` separator lines for visual clarity

### ❌ DON'T:
- Skip heading levels (don't go from # directly to ###)
- Use too many levels (limit to 3-4 levels deep)
- Make headings too long for the TOC
- Place TOC in the middle of content

---

## How It Looks

When you add `{:toc}`, Jekyll generates:
```
1. Section 1
   1.1 Subsection 1.1
       1.1.1 Sub-subsection
   1.2 Subsection 1.2
2. Section 2
   2.1 Subsection 2.1
3. Section 3
```

Each item links to the corresponding heading.

---

## For Your Java Files

Here's how to add TOC to your existing Java files:

**Current format:**
```markdown
---
layout: default
title: "JVM (Java Virtual Machine)"
parent: "Java Fundamentals"
nav_order: 1
permalink: /java/jvm/
---

# ☕ JVM (Java Virtual Machine)

## What is the JVM?
...
```

**Add TOC:**
```markdown
---
layout: default
title: "JVM (Java Virtual Machine)"
parent: "Java Fundamentals"
nav_order: 1
permalink: /java/jvm/
---

# ☕ JVM (Java Virtual Machine)
{: .no_toc }

## Table of Contents
{:toc}

---

## What is the JVM?
...
```

---

## Testing Your TOC

Once deployed to GitHub Pages:
1. The TOC appears as clickable links
2. Clicking a link jumps to that section
3. The TOC is automatically updated from your headings
4. No manual maintenance needed

---

## Jekyll Configuration (Optional)

If TOC doesn't appear, check `_config.yml` has Kramdown configured:

```yaml
markdown: kramdown
kramdown:
  parse_block_html: true
  toc_levels: 1..3
```

---

## Quick Summary

| Feature | Code | Result |
|---------|------|--------|
| Generate TOC | `{:toc}` | Automatic clickable table of contents |
| Exclude heading | `{: .no_toc }` | Heading won't appear in TOC |
| Custom ID | `{: #id }` | Custom URL anchor |
| Separator | `---` | Horizontal line |

---

**Now you're ready to add table of contents to all your markdown files!**

