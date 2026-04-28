# 📖 Right-Side TOC Guide for Markdown Files

This site uses the `just-the-docs` theme, so the right-side table of contents is generated automatically from page headings.

---

## How It Works

You do **not** need to add inline TOC markup like `{:toc}`.

The right sidebar TOC is built from:
- `##` major sections
- `###` subsections

---

## Recommended Markdown Structure

```markdown
---
layout: default
title: "Your Page Title"
parent: "Parent Section"
nav_order: 1
permalink: /your-page/
has_toc: true
---

# Your Page Title

## Overview
Content here...

## How It Works
Content here...

### Key Detail
Content here...

## Best Practices
Content here...
```

---

## Rules for TOC to Appear

1. Use normal markdown headings
   - `#` for page title
   - `##` for main sections
   - `###` for subsections

2. Do not skip levels
   - Good: `#` → `##` → `###`
   - Avoid: `#` → `####`

3. Keep `has_toc: true` in frontmatter

---

## What Not to Add

You do **not** need:

```markdown
## Table of Contents
{:toc}
```

That creates an inline TOC inside the page body, which is different from the theme's right sidebar TOC.

---

## For Java Topic Pages

Use section headings like this:

```markdown
# ☕ JVM (Java Virtual Machine)

## Textbook Definition

## Simple Definition

## First Principles Explanation

## Mental Model

## How It Works

## Common Misconceptions

## Pitfalls in Production
```

This is the structure now used in the Java pages so the right-side TOC can render.

---

## Validation Checklist

- Page has frontmatter
- Page has `has_toc: true`
- Page contains `##` headings
- Site is rebuilt on GitHub Pages
- Page is viewed on a wide enough screen for the right sidebar

---

## If TOC Still Does Not Show

Check these first:
- the page actually has section headings
- the site rebuild completed after the change
- browser cache is refreshed
- you are looking at a docs page, not only the left navigation tree

---

## Summary

For this site, the simplest rule is:

**Write clean `##` and `###` headings, keep `has_toc: true`, and let the theme generate the right-side TOC automatically.**
