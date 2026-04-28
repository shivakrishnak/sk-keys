# Markdown Template for Automatic Right-Side TOC

Use this template for new markdown files in this site.

---

## Standard Template

```markdown
---
layout: default
title: "Your Page Title"
parent: "Parent Section Name"
nav_order: 1
has_toc: true
permalink: /your-section/your-page/
---

# Your Page Title

## Overview

## Core Concepts

## How It Works

### Important Detail

## Examples

## Best Practices
```

---

## Java Topic Template

```markdown
---
layout: default
title: "Your Topic"
parent: "Java Fundamentals"
nav_order: 12
has_toc: true
permalink: /java/your-topic/
---

# ☕ Your Topic

## Textbook Definition

## Simple Definition

## First Principles Explanation

## Mental Model

## How It Works

## Common Misconceptions

## Pitfalls in Production

## Related Keywords
```

---

## Other Section Template

```markdown
---
layout: default
title: "Your Topic"
parent: "Section Name"
nav_order: 1
has_toc: true
permalink: /section/topic/
---

# Your Topic

## Introduction

## Core Concepts

## Implementation

### Example

## Advanced Topics

## Best Practices
```

---

## Important Notes

- The theme generates the right-side TOC automatically
- Use `##` for major sections
- Use `###` for subsections
- Avoid jumping from `#` directly to `####`
- Keep `has_toc: true` in frontmatter

---

## Do Not Add Inline TOC Markup

Do not add this unless you intentionally want an inline TOC inside the content:

```markdown
## Table of Contents
{:toc}
```

For this site, the preferred approach is the automatic right-side TOC only.

---

## Quick Checklist

- frontmatter present
- `has_toc: true`
- meaningful `##` headings
- optional `###` subsections
- clean permalink

---

## Result

Once deployed, the page will show:
- left navigation menu for site structure
- right-side TOC for the current page sections
- heading anchor links
