---
id: LNX-002
title: The Open Source Revolution (GNU, Linux, FSF)
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-001
used_by: LNX-003, LNX-111
related: LNX-001, LNX-109, LNX-110
tags: [open-source, GNU, GPL, FSF, history, philosophy]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 2
permalink: /technical-mastery/lnx/open-source-revolution/
---

## TL;DR

The Open Source Revolution was the result of two independent
movements converging: Richard Stallman's GNU Project (1983) to
create free Unix tools, and Linus Torvalds' Linux kernel (1991)
to fill the missing kernel gap. Together they created the free,
open-source software ecosystem that now powers the internet. The
GPL license is the legal mechanism that keeps it open.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-002 |
| **Difficulty** | ★☆☆ Orientation |
| **Category** | Linux |
| **Tags** | open source, GNU, GPL, FSF, free software, history |
| **Prerequisites** | LNX-001 |

---

### The Problem This Solves

In the late 1970s and early 1980s, software sharing was normal.
AT&T gave away Unix source code to universities. Hackers at MIT's
AI Lab routinely shared programs. Then corporations discovered
software could be a product. AT&T started enforcing Unix copyright
in 1979. Companies began adding software license restrictions that
prevented copying, studying, modifying, and redistributing code.

Richard Stallman, an MIT AI Lab hacker, was infuriated when he
couldn't fix a bug in the code for a printer because the source
was proprietary. He began the GNU Project in 1983 to create a
completely free (as in freedom) Unix-compatible operating system.

By 1991, GNU had almost everything: gcc compiler, glibc, bash shell,
grep, sed, awk, make. It was missing one piece: the kernel. Hurd
(the GNU kernel) was years from being ready.

Linus Torvalds announced his Linux kernel. Combined with GNU tools,
the complete free operating system finally existed.

---

### Textbook Definition

**Free Software** (as defined by FSF): software where users have the
freedom to run, study, modify, and distribute it. "Free" means freedom,
not price ("free as in freedom, not as in free beer").

**Open Source Software**: software with publicly available source code.
Similar to free software in practice but with different philosophical
framing (pragmatic vs. ideological).

**GNU General Public License (GPL)**: a "copyleft" license that grants
the four freedoms but requires any derivative works distributed to others
also be licensed under GPL. This prevents corporations from taking open
source code, making improvements, and releasing only the binaries.

**GNU Project**: started by Richard Stallman in 1983 to create a
complete free Unix-like operating system. GNU is a recursive acronym:
"GNU's Not Unix."

---

### Understand It in 30 Seconds

```
The problem: AT&T owns Unix; everyone must pay or can't use it
     |
     v
1983: Stallman starts GNU Project: "We'll build a free Unix"
     |
     | GNU creates: gcc, bash, glibc, coreutils, emacs, etc.
     v
1991: GNU has all tools but NO KERNEL (Hurd not ready)
     |
     | Torvalds announces Linux kernel
     v
GNU + Linux = Complete free operating system
     |
     | GPL license protects it: modifications must stay free
     v
Thousands of contributors worldwide
Distributions package GNU+Linux for users
Result: powers 96% of world's web servers
```

---

### First Principles

**The Four Freedoms (FSF definition):**
- Freedom 0: Run the program for any purpose
- Freedom 1: Study how the program works (source code required)
- Freedom 2: Redistribute copies
- Freedom 3: Distribute modified versions

**Copyleft (the GPL mechanism):**
GPL is "copyleft" - the opposite of copyright's restriction.
Copyright: I own this, you cannot use/copy/modify it.
Copyleft: Use/copy/modify freely, BUT any distribution of
derivatives must grant the same freedoms to recipients.

This is the viral property of GPL: any software linked
with GPL code must itself be GPL (with some exceptions).
This prevents the "embrace and extend" strategy corporations
used with open standards.

**Why this was radical in 1983:**
Software was becoming proprietary. Stallman's insight: if
freedom is the goal, the license must legally protect it.
Not just "please don't make this proprietary" - but a legal
framework that makes it impossible while still allowing use.

---

### Thought Experiment

Imagine a recipe book that says "You may use these recipes freely,
but if you publish a cookbook using any of these recipes, your
cookbook must also be freely shareable."

That's GPL. The recipe (source code) spreads freely. Anyone
building on it must share their additions equally. A corporation
cannot take the cookbook, add 10 new recipes, and sell a locked
version where others cannot see the recipes.

Now imagine some people disagree: "I want to share freely but
allow corporations to use my recipe without giving back." That's
BSD/MIT license (permissive). Apache, Node.js, React: MIT/Apache
licensed. Linux kernel: GPL. The philosophical difference has
practical engineering consequences: companies building embedded
products prefer BSD so they don't have to open-source their changes.

---

### Mental Model / Analogy

Think of the open source ecosystem as a **commons** - shared land
that everyone can use and improve:

```
GPL (Linux kernel, GCC) = Preserved commons
  Anyone can use the land (run the software)
  Anyone can improve it (modify)
  But: you cannot fence it off (distribute must be open)
  Protects against: tragedy of the enclosures
  
MIT/BSD/Apache = Open commons
  Anyone can use the land
  Anyone can improve it
  AND: you can fence off your improvements (keep proprietary)
  Risk: corporation may build on commons then charge for access
  
Creative Commons = Same concept for content
```

The GPL commons has produced Linux, GCC, Git, MySQL (GPL version),
and the entire GNU toolchain. The MIT/BSD commons produced Node.js,
React, Python, FreeBSD, and macOS (BSD lineage).

---

### Gradual Depth - Five Levels

**Level 1 (student):**
Open source means the code is public. GNU/Linux means you
get a complete computer operating system for free. The GPL
license means it stays free even when companies use it.

**Level 2 (developer):**
GPL requires any software you distribute that links against
GPL code to also be GPL. This is why device manufacturers
who ship Linux must release their kernel modifications.
(They often don't - this is a compliance issue in embedded.)

**Level 3 (senior):**
GPL v2 (Linux kernel) vs GPL v3 (newer GNU tools):
GPL v3 adds anti-tivoization clause (prevents using signed
bootloaders to prevent running modified software on hardware).
Linux kernel chose NOT to upgrade to v3 - Torvalds specifically
rejected this, which is why Android (AOSP) companies can lock
bootloaders while technically complying with GPL v2.

**Level 4 (expert/legal):**
Kernel module licensing: a kernel module MUST be GPL (or GPL-
compatible) to be distributed, OR must use a special exception
(like NVIDIA's dual kernel interface approach). NVIDIA avoids
GPL by using a thin GPL "shim" that interfaces with their
proprietary blob. The Linux community considers this a violation
of GPL spirit. Linus Torvalds has been vocal about this.

**Level 5 (architect/policy):**
License compatibility matters for enterprise software stacks.
GPL + Apache 2.0 in the same binary: problematic (ASF and FSF
consider these incompatible). LGPL: lesser GPL allows linking
without the copyleft obligation (designed for libraries). AGPL:
like GPL but closes the "service loophole" (SaaS providers must
publish modifications even if not distributing software).

---

### How It Works

```
GPL License Mechanism:

Author releases code under GPL:
  -> Source must be available when distributing binaries
  -> License text must accompany distribution
  -> Recipients get the same rights (chain preserved)
  
Distribution triggers GPL obligations:
  -> "Distribution" = giving software to someone else
  -> Running software as SaaS (cloud) does NOT trigger GPL
     (this gap led to AGPL: Affero GPL)
  
Derivative work determination:
  -> Static linking: almost always derivative work
  -> Dynamic linking: depends on court interpretation
  -> Separate process (IPC): usually NOT derivative
  -> Kernel modules: GPL requires GPL (with exceptions)
  
GPL enforcement:
  -> Copyright holders can sue for violation
  -> Most cases: compliance demand before litigation
  -> Software Freedom Conservancy: active GPL enforcer
  -> BusyBox violations: multiple cases settled
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Open source = free (no cost)" | Open source means freedom to use/modify/distribute. Cost is separate. Red Hat charges for support of open source software. |
| "GPL means I can't use Linux commercially" | GPL allows commercial use. Red Hat, SUSE, Canonical run billion-dollar businesses on GPL software. You cannot make Linux proprietary and sell it without source code. |
| "Linux is owned by Linus Torvalds" | The Linux kernel is owned by its contributors collectively (copyright law). Torvalds holds the trademark "Linux" and the kernel's moral authority, not ownership. |
| "GNU and Linux are the same project" | GNU (Stallman, FSF) and Linux (Torvalds) are separate projects with different philosophies. They combined to create the OS but are maintained independently. |
| "Open source is more secure because many eyes review it" | This is "Linus's Law" in theory. In practice: Heartbleed was in OpenSSL for 2 years undetected. Open source security depends on actual reviewers, not just public availability. |

---

### Failure Modes & Diagnosis

**GPL compliance violation (distribution without source):**
```
Symptom: Shipping a Linux-based product (router, device) 
         without making kernel modifications available
Fix: 
  1. Identify all GPL components in your build
  2. Provide written offer for source code (5-year validity)
  3. Include GPL license text with product
Tools: FOSSology, Scancode for license scanning
```

**License incompatibility in software stack:**
```
Symptom: Legal team flags GPL code in commercial product
         where EULA prohibits source disclosure
Analysis:
  1. Is the GPL code dynamically linked? (less clear)
  2. Is it statically linked? (almost certainly derivative work)
  3. Is it a separate process communicating via IPC? (usually OK)
Fix: Replace GPL component with MIT/Apache alternative
     OR obtain commercial license (MySQL, Qt offer this)
```

**Security:** Open source does not guarantee security.
```
Historical lessons:
  Heartbleed (OpenSSL 2014): missed for 2 years in open code
  Log4Shell (Log4j 2021): critical RCE in widely-used library
  XZ Utils (2024): supply chain attack via malicious contributor
  
Lesson: Open source requires active security review programs,
not just availability of source code.
```

---

### Related Keywords

**Foundational:**
LNX-001 (What Linux Is), LNX-109 (Linus Torvalds),
LNX-110 (GNU/Linux Story), LNX-111 (Kernel Architecture)

**Builds on this:**
LNX-003 (Linux in Production), LNX-004 (Linux vs alternatives)

**Related across categories:**
SEC-001 (Software Supply Chain Security), GIT-001 (Git)

---

### Quick Reference Card

| Item | Value |
|------|-------|
| GNU started | 1983 by Richard Stallman |
| Linux kernel | 1991 by Linus Torvalds |
| GPL v2 (kernel) | Copyleft, distribution triggers source requirement |
| GPL v3 | Adds anti-tivoization; Linux kernel did NOT adopt |
| MIT/Apache | Permissive; corporations can keep modifications proprietary |
| LGPL | Allows linking without copyleft for libraries |
| AGPL | GPL + service loophole closed (SaaS must release) |
| Enforcement | Copyright holders via Software Freedom Conservancy |
| FSF | Free Software Foundation; defines four freedoms |

**3 things to remember:**
1. GPL copyleft = viral; derivatives must stay open
2. GNU made the tools; Linux made the kernel; together = OS
3. Open source doesn't automatically mean secure - needs active review

**Interview angle:**
"If a company builds a proprietary product using Linux kernel,
what are their GPL obligations?" -> Must release kernel source
modifications; binaries alone violate GPL. Cannot make the kernel
itself proprietary. User-space applications above the kernel can
be proprietary (kernel syscall interface exception).

---

### Transferable Wisdom

The **copyleft mechanism** is a creative legal hack: using
copyright law to guarantee the opposite of copyright's usual
effect. This pattern appears in software licenses, creative
commons, and data sharing agreements.

The **commons model** of open source predicts two things:
1. Tragedy of the commons (free-riders degrade the resource)
   - Prevented by GPL: contributors must give back
   - But still happens: OpenSSL (critical infrastructure, 2 FTE)
2. Virtuous cycles: more users -> more contributors -> better software
   - Linux: more users -> IBM/Red Hat invest -> better kernel

For engineers building platforms: **license choice** is an
architectural decision with long-term consequences. GPL prevents
proprietary forks but may deter enterprise adoption. MIT/Apache
accelerates adoption but allows proprietary forks (e.g., Amazon
forked ElasticSearch when Elastic changed to SSPL).

---

### The Surprising Truth

Richard Stallman's GNU Project, started in 1983, was supposed to
produce both the tools AND the kernel. The tools (gcc, bash, glibc)
succeeded brilliantly. The kernel (GNU Hurd) is still in development
43 years later and has never been used in production by anyone. The
GNU tools that power Linux are Stallman's success. The kernel he
planned to build never materialized, and instead a 21-year-old Finnish
student's "hobby" became the most important kernel in history.

---

### Mastery Checklist

- [ ] Can explain the four freedoms of free software
- [ ] Can describe the difference between GPL and MIT licenses
- [ ] Can explain the copyleft mechanism and why it's "viral"
- [ ] Can distinguish the GNU Project from the Linux kernel project
- [ ] Can explain what triggers GPL obligations during software distribution

---

### Think About This

1. Amazon Web Services runs their infrastructure on Linux (GPL)
   but is not required to release their custom kernel patches.
   Under what conditions did this become controversial, and what
   license change could force them to open source their changes?

2. The Linux kernel chose GPL v2 and explicitly rejected GPL v3.
   Torvalds said v3 was "too restrictive." What specific provision
   in GPL v3 concerned him, and how does this affect Android device
   manufacturers who lock bootloaders?

3. If Stallman had succeeded with GNU Hurd instead of Torvalds with
   Linux, the kernel would have been under GPL v3 (or its predecessor).
   How might this have changed the cloud computing industry?

**TYPE G:** Open source has a supply chain problem: critical
infrastructure (OpenSSL, Log4j, XZ Utils) is maintained by
volunteers with minimal resources while companies worth billions
depend on it. How should the industry restructure funding for
open source infrastructure? What models (foundations, bounties,
corporate mandates) have been tried and what are their trade-offs?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the GPL license and why does it matter for engineers?
A: GPL (General Public License) is a copyleft license that grants freedom to use, study, modify, and distribute software, with one requirement: any distributed derivative works must also be GPL-licensed. For engineers: if your product ships a GPL library or kernel module, you must provide source code. The Linux kernel is GPL v2, meaning companies that ship Linux devices (routers, phones, embedded systems) must release their kernel modifications - though compliance is often poor.

**Intermediate:**
Q: What is the difference between GPL, LGPL, MIT, and Apache 2.0 licenses?
A: GPL (copyleft, viral - derivatives must be GPL), LGPL (Lesser GPL - can be dynamically linked without copyleft obligation, designed for libraries), MIT (permissive - can use in proprietary projects, no distribution requirements), Apache 2.0 (permissive + explicit patent license grant - common in enterprise open source). For enterprise software: Apache 2.0 is generally safest. For a library you want widely adopted: LGPL or MIT. For a project where you want to prevent proprietary forks: GPL or AGPL.

**Expert:**
Q: A company ships a network appliance running a custom Linux kernel. What are their exact GPL obligations, and how might they violate them?
A: They must: (1) make all GPL kernel source code available (their modifications to the Linux kernel), (2) include the GPL license text, (3) provide either the full source or a written offer valid for 3 years. Common violations: shipping binaries without source offer, shipping source for an older kernel version than the one running, including proprietary kernel modules without the GPL exception that the module loader enforces. The SFLC and Software Freedom Conservancy actively enforce these - BusyBox and Linux have been the subjects of multiple successful enforcement actions.
