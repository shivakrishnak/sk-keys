---
id: LNX-110
title: "The GNU/Linux Story (Stallman, GPL, Free Software)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-001, LNX-109
used_by: LNX-111
related: LNX-001, LNX-109, LNX-111, LNX-112
tags: [gnu, richard-stallman, free-software, gpl, copyleft, four-freedoms, fsf, open-source, osi, eric-raymond, gnu-tools, gcc, glibc, bash, coreutils, emacs, gnu-hurd, lgpl, agpl, license-compatibility, android-linux, tivoization, cathedral-bazaar, linux-naming]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 110
permalink: /technical-mastery/lnx/gnu-linux-story-stallman-gpl-free-software/
---

## TL;DR

In 1983, Richard Stallman (MIT AI Lab hacker) launched the **GNU Project** to
create a completely free Unix-like OS. By 1991: GNU had all the tools (GCC compiler,
glibc C library, bash shell, coreutils: ls, cp, mv, grep) but no kernel - GNU Hurd
was unfinished. Linux (1991) provided the missing kernel. **GNU/Linux = GNU tools +
Linux kernel = complete free OS**. The legal framework: **GPL** (General Public
License) - Stallman's invention of "copyleft" - requires any derivative work to also
be GPL, ensuring all improvements remain free. The **Four Freedoms**: run, study,
modify, distribute. Tension: Stallman's naming insistence (GNU/Linux, not Linux)
vs Torvalds's dismissal. Fork: **Open Source** (Eric Raymond, OSI, 1998) dropped
freedom philosophy, focused on practical benefits - this is how most developers
encounter it today. **License compatibility matrix** matters: GPL v2 modules in a
GPL v2 kernel (compatible), Apache 2.0 + GPL v2 (incompatible, Apache has patent
clause), LGPL + proprietary (compatible by design). Android uses this: Linux kernel
(GPL v2) + Apache-licensed Android framework = Google does not have to open-source
non-kernel code.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-110 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | GNU, Stallman, GPL, copyleft, free software, open source, four freedoms, FSF, OSI, license compatibility |
| **Prerequisites** | LNX-001 (Linux overview), LNX-109 (Torvalds/Linux history) |

---

### The Problem This Solves

**Historical problem**: In 1983, proprietary software was the norm. AT&T Unix
was licensed but heavily restricted. The hacker culture of the 1970s (share
code, study programs, improve and redistribute) was being replaced by
NDAs, binary-only software, and restrictive licenses. Stallman's position:
this was ethically wrong - software should be free to study, modify, and share.

**Present-day context**: Understanding the philosophical and legal foundations
of GNU, GPL, and free software is essential to:
1. Understanding Linux's license correctly (what you can and cannot do)
2. Understanding the license debate that shapes modern open-source projects
3. Understanding the Android legal model (GPL kernel + proprietary apps)
4. Making correct licensing decisions when distributing software

---

### Textbook Definition

**Free Software** (FSF definition): Software that respects users' freedom and
community. The Four Freedoms:
- **Freedom 0**: Run the program, for any purpose
- **Freedom 1**: Study how the program works and change it (requires source code)
- **Freedom 2**: Redistribute copies to help others
- **Freedom 3**: Distribute copies of your modified versions

**Note**: "Free" is about freedom, not price. "Free as in speech, not free as in beer."

**GPL (General Public License)**: A software license embodying copyleft. GPL
ensures: anyone who distributes GPL software must provide source code AND must
license the distributed software under GPL. This "virality" ensures improvements
to GPL software remain free and available to all.

**Copyleft**: A licensing strategy that uses copyright law "in reverse" to
ensure software remains free. Copyright normally restricts what you can do with
software. Copyleft uses copyright to restrict RESTRICTIONS: you may distribute
but cannot add restrictions (including "must keep proprietary").

---

### Understand It in 30 Seconds

```bash
# === GNU tools on a modern Linux system ===

# GNU tools are what you use every day on Linux:
ls --version
# ls (GNU coreutils) 8.32
# Copyright (C) 2020 Free Software Foundation, Inc.
# License GPLv3+: GNU GPL version 3 or later

bash --version
# GNU bash, version 5.1.16(1)-release (x86_64-pc-linux-gnu)
# Copyright (C) 2020 Free Software Foundation, Inc.

gcc --version
# gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0
# Copyright (C) 2021 Free Software Foundation, Inc.

# GNU = GNU is Not Unix (recursive acronym)
# All these tools existed BEFORE Linux!
# In 1991: GNU had tools, Linux had the kernel
# Together: complete OS

# === Check licenses of software on your system ===
dpkg -l | grep -i license
# Most packages list their license in debian/copyright

# Check license of a specific package:
cat /usr/share/doc/bash/copyright | head -20
# GNU Bash is Copyright (C) ... under the terms of the GNU General
# Public License as published by the Free Software Foundation

# === GPL implications for kernel modules ===

# A kernel module (device driver) must be GPL-compatible:
cat hello_module.c
# #include <linux/module.h>
# MODULE_LICENSE("GPL");  <- REQUIRED for kernel module
# MODULE_AUTHOR("Example");
# MODULE_DESCRIPTION("Hello World Module");
# 
# static int __init hello_init(void) { ... }
# static void __exit hello_exit(void) { ... }
# module_init(hello_init);
# module_exit(hello_exit);

# Non-GPL module: "tainted" kernel
modinfo nvidia_drm | grep license
# license: MIT  <- not GPL!
# Loading this: kernel marks itself as "tainted"
dmesg | grep -i tainted
# [  3.245678] nvidia: module license 'MIT' taints kernel.

# Tainted kernel: kernel developers may not help debug issues
# because they can't see the proprietary module's source

# === The GNU Naming Dispute ===

# In 2021, Stallman publicly:
# "The system people call Linux is really GNU with Linux added"
# "I ask that you call the system GNU/Linux"

# Torvalds's response:
# "I'd hope the GNU/Linux thing would die down...
#  I think calling the kernel Linux is fine,
#  and calling the entire OS 'Linux' is fine"

# Practical convention:
# "Linux": the kernel (technically correct, Torvalds's preference)
# "GNU/Linux": the OS = kernel + GNU userland (FSF/Stallman's preference)  
# "Ubuntu", "Fedora", "Debian": distributions (practical daily usage)
# All correct in different contexts; choose based on audience
```

---

### First Principles

```
HOW STALLMAN'S APPROACH DIFFERED FROM TORVALDS'S:

Stallman (1983 GNU Project):
  Motivation: MORAL
  "It is wrong to prevent people from sharing software"
  "All software should be free (as in freedom)"
  Approach: complete, principled, designed from scratch
  Method: one programmer (Stallman), wrote Emacs, GCC, etc.
  Goal: complete free Unix replacement (GNU = GNU's Not Unix)
  Timeline: slow (principled design takes time)
  
Torvalds (1991 Linux):
  Motivation: PRACTICAL
  "I need a Unix kernel for my 386, Minix is too limited"
  "Free" was nice but not the primary motivation
  Approach: pragmatic, iterative, "good enough and improving"
  Method: community-driven from day one
  Goal: working Unix-compatible system (not ideologically motivated)
  Timeline: fast (working system in months)

The synthesis: GNU/Linux
  GNU provided: principled, high-quality core tools
  Linux provided: pragmatic, working kernel
  Together: complete OS that was BOTH free (freedom) AND practical
  
  This explains why:
  - GNU tools are high quality (Stallman's principled engineering)
  - Linux kernel moves fast (Torvalds's practical approach)
  - They sometimes conflict (GPL v2 vs GPL v3, naming dispute)

THE FOUR FREEDOMS: why they matter in practice

Freedom 0 (Run): No restriction on use
  Without: software licensed "for educational use only"
  With: company can use GNU/Linux for commercial servers
  
Freedom 1 (Study): Can read source code and understand it
  Without: you use a black box - you cannot know what it does
  Security implication: you must trust the vendor
  With: Heartbleed (OpenSSL bug, 2014) was found and fixed by the community
  (you could READ the SSL code and find the bug)
  
Freedom 2 (Redistribute): Can share the software
  Without: one copy per license, no sharing
  With: you can give Ubuntu CDs to friends (or ship them AWS AMIs)
  
Freedom 3 (Distribute modifications): Can improve and share
  Without: your improvements benefit only you
  With: your fix for a kernel bug benefits everyone
  GPL adds: you MUST share under GPL (copyleft adds obligation to the freedom)

HOW COPYLEFT WORKS (the mechanism):

Copyright law: creator has exclusive rights (cannot copy, modify, distribute
                without permission)
               
Standard license: grants permission to use, maybe distribute (restrictions vary)

GPL copyleft mechanism:
  "You have permission to copy, modify, and distribute this software
   PROVIDED THAT: you distribute the same rights to your recipients"
   
  Translation: "you can fork GPL software, but your fork must also be GPL"
  
  Why "viral" (critics) / "freedom-preserving" (supporters):
  GPL spreads through the software supply chain
  Library A is GPL -> Software B links to A -> Software B must be GPL
  
  This is the key controversy:
  Pro: ensures all improvements benefit the public
  Con: cannot link GPL libraries into proprietary software
  
  LGPL (Lesser GPL): compromise:
  Library is LGPL -> proprietary software CAN link to it
  But: modifications to the LGPL library itself must be LGPL
  Used by: glibc (C library), Qt (with commercial license option)

THE OPEN SOURCE FORK (1998):

Eric Raymond, Bruce Perens: co-founded OSI (Open Source Initiative)
Motivation: "Free software" language scared businesses
  "Free" -> business owners heard "zero cost" (wrong) or "no copyright" (wrong)
  "Open Source" -> "you can see and verify the code"
  
OSI Open Source Definition: 10 criteria (similar to Four Freedoms but...)
  Omits: freedom as a moral obligation
  Focus: practical benefits (reliability, security, innovation)
  
Business impact:
  OSI rebranding: companies like IBM, Sun, Netscape adopted open source
  Without OSI: corporate adoption of Linux may have been slower
  With OSI: "open source" became business-friendly, Linux won servers
  
The divergence:
  FSF/Stallman: freedom is a moral imperative; "open source" is too pragmatic
  OSI/Raymond: freedom is a side-effect of good engineering practice
  
  Today: majority of developers use "open source" language
  Stallman: continues to insist on "free software" language
  Practical consequence: mostly naming; both camps use same licenses (GPL, MIT, etc.)

LICENSE COMPATIBILITY: the critical practical problem

When combining software from different projects:
  Project A: GPL v2
  Project B: Apache 2.0
  Combined binary: ???

GPL v2 says: entire work must be GPL v2
Apache 2.0 says: may add conditions (patent clause not in GPL v2)

Problem: Apache 2.0's explicit patent grant is an "additional condition"
         GPL v2 says: "you may not impose additional restrictions"
         Therefore: GPL v2 and Apache 2.0 are INCOMPATIBLE for combined works

Practical impact: 
  Cannot link an Apache 2.0 library into a GPL v2 kernel module
  Cannot link a GPL v2 library into an Apache 2.0 application (and distribute)
  
  EXCEPTION: kernel uses "SPDX" to track per-file licenses
  User-space API headers (uapi): special exception, can be used by any program
  
GPL v2 + MIT: COMPATIBLE (MIT allows any use, including GPL v2)
GPL v2 + LGPL v2.1: COMPATIBLE (designed to be)
GPL v2 + GPL v3: INCOMPATIBLE (different versions have different terms)
  - "GPL v2 or later" code: can use v3
  - "GPL v2 only" (Linux kernel): CANNOT combine with GPL v3 code
  
Android's clever solution:
  Linux kernel: GPL v2 (must release kernel modifications)
  Android user-space: Apache 2.0 (no copyleft: proprietary apps OK)
  Bionic libc: Apache 2.0 (replaces glibc, no GPL copyleft to user space!)
  Result: device manufacturer can run AOSP + proprietary apps legally
```

---

### Thought Experiment

The Android case study in GPL compliance vs freedom:

```bash
# === Android: GPL v2 kernel + Apache user space ===

# What Google releases (AOSP - Android Open Source Project):
# 1. Linux kernel modifications: GPL v2 (required by law)
# 2. Android framework (Java/Kotlin APIs): Apache 2.0 (not required, Google's choice)
# 3. AOSP apps (Contacts, Calendar, basic apps): Apache 2.0

# What Google does NOT have to release (and doesn't):
# Google Play Services: proprietary
# Google Maps app: proprietary  
# Gmail app: proprietary
# Google Assistant: proprietary

# The key: Android's Bionic libc (C library replacement)
# glibc (GNU C library): LGPL v2.1
#   Programs that link against LGPL code: can be proprietary
#   BUT: LGPL programs themselves must share modifications to the library

# Android's Bionic: Apache 2.0
#   Programs that link against Apache 2.0 code: fully proprietary OK
#   No copyleft at any level (except kernel, which is isolated)

# Is this "free software" in Stallman's sense?
# NO: you can't run a different kernel on most Android phones (locked bootloader)
# NO: Google Play Services is proprietary and apps depend on it
# Technically legal: GPL v2 kernel source released; user space is Apache choice

# Stallman's critique of Android:
# "Android is not free software in the sense of freedom"
# "It respects some freedoms but not others"
# "Users have freedom 0 (run) but not always freedom 3 (modify and run)"

# Torvalds's view:
# "I don't care if Android doesn't give users root access"
# "I care that the kernel modifications are released (GPL compliance)"
# These are opposite views of what "free" means for an OS

# === Checking GPL compliance in practice ===

# How to verify Android device releases kernel source:
# Kernel source must be available for 3 years (GPL v2 requirement)
# For Samsung Galaxy: developer.samsung.com/samsung-open-source
# For Google Pixel: android.googlesource.com/kernel

# Check your Android phone's kernel version (from phone):
# Settings > About Phone > Kernel Version
# 5.15.104-android13-9-00001  <- this kernel's source must be available

# Request source if not provided:
# GPL v2 Section 3: written offer for source code, valid for 3 years
# If manufacturer refuses: GPL violation, can be reported to Software Freedom
# Conservancy (SFC) or FSF - both enforce GPL
```

---

### Mental Model / Analogy

```
The recipe analogy (Stallman's favorite):

Proprietary software = restaurant with secret recipes:
  You can EAT the food (run the program)
  You CANNOT see the recipe (read the source code)
  You CANNOT teach others the recipe (distribute source)
  You CANNOT adapt it (modify for your needs)
  If restaurant closes: recipe lost forever
  If recipe has poison: you cannot detect it

Free software = recipe shared in a cookbook:
  You can COOK it (run the program)
  You can READ and STUDY the recipe (read source)
  You can SHARE the cookbook (redistribute)
  You can ADAPT the recipe (modify and distribute)
  
GPL copyleft = "share-alike" recipe license:
  You can share the cookbook (distribute)
  But: you MUST publish your adaptations under same license
  Your private variations: you can keep private
  But: once you share an adapted dish commercially -> must share recipe
  
BSD/MIT/Apache = more permissive recipe license:
  Take recipe, modify it, sell the result (without sharing recipe)
  Build a restaurant with secret improvements
  Example: Apple uses BSD network stack (modified, kept proprietary)
  
LGPL = cookbook for special ingredient (library):
  The ingredient (library) is shared freely
  Your dish (application) can be proprietary
  But: if you modify the ingredient recipe: must share that change
  
The "missing ingredient" problem (1991):
  GNU had all recipes: compiler (GCC), shell (bash), utensils (coreutils)
  GNU had NO oven (kernel) - GNU Hurd was still being designed
  
  Linux: built an oven (kernel) in 1991
  Under GPL v2 (share-alike): improvements must be shared
  
  The GNU/Linux meal: GNU utensils + GNU recipes + Linux oven = complete kitchen
  Now anyone can run a free software restaurant

The Four Freedoms as rights:
  Freedom 0 (Run): right to eat in any restaurant
  Freedom 1 (Study): right to know what's in your food (ingredients label)
  Freedom 2 (Redistribute): right to share food with others
  Freedom 3 (Modify/Distribute): right to adapt recipes and share them
  
  GPLv3 Tivoization clause: right to cook in your own kitchen
  (not just receive recipes: actually be able to modify your device)
  Torvalds: "I don't insist on this freedom for kernel" (GPL v2 only)
  Stallman: "Without this, freedom 3 is incomplete for locked devices"

Open Source vs Free Software:
  Free Software = restaurant that believes sharing recipes is a moral right
  Open Source = restaurant that believes showing recipes attracts better chefs
  Both share recipes. Different reason. Same practical outcome (mostly).
```

---

### Gradual Depth - Five Levels

**Level 1:**
GNU Project: Stallman, 1983, goal was complete free Unix. Four Freedoms.
GPL = copyleft: software remains free. GNU tools: bash, GCC, coreutils.
GNU + Linux = complete OS. Open source vs free software: same thing mostly.

**Level 2:**
How copyleft works: copyright reversed, derived works must be GPL. GPL v2
key clauses: source code distribution, no additional restrictions. LGPL:
weaker copyleft for libraries. The naming dispute: GNU/Linux vs Linux.
OSI and open source definition. Why Android can have proprietary apps on
GPL Linux kernel. GPL violations and enforcement.

**Level 3:**
License compatibility matrix: GPL v2 + MIT, GPL v2 + Apache 2.0 (incompatible),
GPL v2 + GPL v3 (incompatible, "or later" clause). AGPL (Affero GPL): closes
the "ASP loophole" (GPL allows running modified GPL code as a service without
releasing source; AGPL requires source release for network services). GPL v3:
Tivoization clause, patent retaliation clause. Why kernel is GPL v2 only.

**Level 4:**
GPL enforcement: Software Freedom Conservancy (SFC) vs FSF as enforcers.
License notices requirements: what must appear in binary distributions. SPDX
(Software Package Data Exchange): standardized machine-readable license IDs.
Kernel module licensing: EXPORT_SYMBOL_GPL vs EXPORT_SYMBOL (GPL-only symbols).
OpenSSL exception: why kernel can link OpenSSL despite license mismatch.

**Level 5:**
Copyleft theory: Benjamin Mako Hill's work on copyleft as political strategy.
License proliferation problem: OSI has approved 80+ licenses, compatibility
nightmare. REUSE specification for per-file SPDX compliance. The "network
effect" in open source: why MIT-licensed projects (Docker, Kubernetes, React)
became dominant despite weaker copyleft. EU copyright directive impact on
open source. GPL enforcement case law: MySQL AB vs Progress Software, Jacobsen
v. Katzer (first US appellate case affirming open source license enforceability).

---

### Code Example

```bash
# === License identification in practice ===

# SPDX (Software Package Data Exchange): machine-readable license IDs
# Used in Linux kernel source (every file):
head -5 /usr/src/linux-source-*/kernel/fork.c
# // SPDX-License-Identifier: GPL-2.0-only
# /*
#  *  linux/kernel/fork.c
#  *
#  *  Copyright (C) 1991, 1992  Linus Torvalds
# ^^ clear, machine-readable license identifier

# Common SPDX identifiers you'll encounter:
# GPL-2.0-only   - GPL v2, NO upgrade to v3 (Linux kernel)
# GPL-2.0-or-later - GPL v2 or any later version
# GPL-3.0-only   - GPL v3
# LGPL-2.1-or-later - LGPL v2.1+ (glibc)
# MIT            - MIT license (no copyleft)
# Apache-2.0     - Apache 2.0 (no copyleft, has patent clause)
# BSD-2-Clause   - BSD 2-clause (no copyleft)
# AGPL-3.0-only  - AGPL v3 (copyleft for network services)

# === LGPL: why glibc uses it ===

# glibc is LGPL, not GPL!
# If glibc were GPL: every program that links libc would need to be GPL
# That would make ALL C programs GPL - clearly not intended

# Check glibc license:
dpkg -s libc6 | grep "^License:"
# Hmm, apt has this in copyright:
cat /usr/share/doc/libc6/copyright | head -20
# This package is licensed under the GNU Lesser General Public License

# Why LGPL for glibc:
# Users of libc (nearly all C programs) can keep their code proprietary
# Modifications to glibc itself must be LGPL
# This allows: proprietary apps on GNU/Linux without forcing them to be GPL

# === EXPORT_SYMBOL_GPL: GPL-only kernel symbols ===

# In kernel source: some symbols are GPL-only
# grep in kernel source:
grep -r "EXPORT_SYMBOL_GPL" /usr/src/linux-source-*/kernel/sched/core.c | head -5
# EXPORT_SYMBOL_GPL(set_cpus_allowed_ptr);
# EXPORT_SYMBOL_GPL(task_css_set_check);

# A proprietary kernel module CANNOT use EXPORT_SYMBOL_GPL symbols
# Only GPL-licensed modules can access these APIs
# This is a technical enforcement of the GPL requirement:

# Check from a module which symbols it uses that are GPL-only:
modinfo mymodule.ko | grep "^depends"
# Any dependency on GPL-only symbols: module MUST be GPL

# === Android GPL compliance check ===

# Verify Samsung releases kernel source:
# (example URL pattern - check manufacturer's actual site)
# developer.samsung.com/samsung-open-source/release

# Check kernel version on Android (via ADB):
adb shell cat /proc/version
# Linux version 5.15.104-android13-9-00001 (gcc@xxx) #1 SMP PREEMPT...

# The source for this exact kernel must be available from Samsung
# If not available: file complaint with Software Freedom Conservancy
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Open source and free software are the same thing" | Open source and free software overlap significantly in PRACTICE (most open-source licenses also grant the four freedoms) but differ in PHILOSOPHY and SCOPE. Free software (FSF): freedom is a moral imperative. You should not use non-free software because it restricts your freedom, regardless of practical benefits. Open source (OSI): open development methodology produces better software. Use whatever license and software serves your needs. The difference matters: (1) FSF recommends against using proprietary software even if no free alternative exists. (2) OSI is neutral on proprietary software (just promotes open source). (3) GPL is both "free" and "open source" by both definitions. (4) The Artistic License 1.0 (Perl) was OSI-approved but not FSF-approved (freedom issue with vague clauses). In daily practice: most developers treat them interchangeably. In policy debates (software freedom advocacy), the distinction matters deeply to the FSF. |
| "GPL means your entire project must be open source if you use any GPL library" | GPL copyleft applies ONLY to derivative works that are DISTRIBUTED. Three critical nuances: (1) INTERNAL USE: If you run GPL software internally (your own servers, your own build system), you NEVER have to release source. Running MySQL (GPL) to serve your web app does not require releasing your web app source. AGPL closes this: modifying AGPL code and running it as a network service does require source release. (2) LINKING: GPL "contamination" works through linking and combining into one work. Calling a REST API served by a GPL program does not make your code GPL (separate programs communicating over a network). (3) LGPL LIBRARIES: If the library uses LGPL, you can link it into proprietary software without your code becoming GPL, provided you link dynamically (not statically embedded). Static linking of LGPL library into proprietary binary: may require additional steps per LGPL section 4/5. |
| "Stallman created Linux" | Stallman created the GNU Project, GNU tools (GCC, bash, coreutils, Emacs), and the GPL license. He did NOT create Linux. Linus Torvalds created the Linux kernel. Stallman argues the OS should be called "GNU/Linux" to credit GNU's contribution, but the naming dispute has not been resolved in his favor in popular usage. Stallman's contribution to what most people call "Linux" is enormous: without GCC, there would be no C compiler to compile the Linux kernel. Without bash, no shell. Without glibc, no C standard library. The complete OS is GNU + Linux. But the kernel (the technical component named "Linux") was written by Torvalds. |
| "Using GPL libraries in your project makes ALL your code GPL (including unrelated code)" | GPL copyleft applies to the "program as a whole" - but "as a whole" has a specific meaning. A program that links against a GPL library creates a GPL-covered combined work. BUT: (1) Separate programs in a project that don't link against the GPL library are NOT covered. (2) Scripts that invoke GPL programs via shell commands (not linking) are generally NOT covered. (3) The FSF vs courts: FSF has an expansive view of "derivative work." US courts have not definitively ruled, but tend toward a narrower "linking + significant amount of GPL code copied" view. (4) Practical reality: many projects use GPL libraries without making all code GPL (gray area), relying on LGPL variants when possible. For legal certainty: get a lawyer's opinion for commercial products. For open-source projects: MIT/Apache license + GPL libraries is a common pattern that most interpret as acceptable (separate files, separate linking units, not one "combined program"). |

---

### Failure Modes & Diagnosis

```bash
# === Common GPL compliance failures ===

# FAILURE 1: Shipping binary without source code offer
# Device manufacturer ships ARM device with Linux kernel
# No source code provided with device, no URL in documentation

# This is a GPL v2 violation!
# GPL v2 requires: "provide written offer to provide source code,
#                   valid for 3 years"
# OR: provide physical media with source code

# Enforcement route:
# Report to: Software Freedom Conservancy (sfconservancy.org)
# They: negotiate with manufacturer, legal action if needed
# Outcome: manufacturer releases kernel source (usually compliance over lawsuit)

# FAILURE 2: Static linking of GPL library into proprietary binary
# MyApp (proprietary) statically links libfoo.so which is GPL
# MyApp is distributed to users

# This is a GPL violation: combined binary includes GPL code
# Fix option 1: switch to LGPL-licensed equivalent of libfoo
# Fix option 2: dynamic linking (check LGPL section 4 requirements)
# Fix option 3: relicense MyApp as GPL (often impractical for commercial)
# Fix option 4: negotiate commercial license for libfoo from copyright holder
#               (dual licensing: many libraries offer GPL + commercial license)

# MySQL example of dual licensing:
# MySQL Community Edition: GPL (any project using it must consider GPL implications)
# MySQL Enterprise: commercial license (no copyleft, no source requirement)
# Choice: pay for commercial license OR comply with GPL

# FAILURE 3: Using EXPORT_SYMBOL_GPL in proprietary kernel module
# Error at module load time:

insmod mydriver.ko
# insmod: ERROR: could not insert module mydriver.ko: Unknown symbol in module
dmesg | grep "Unknown symbol"
# mydriver: Unknown symbol sched_setscheduler (err -2)
# ^ sched_setscheduler is EXPORT_SYMBOL_GPL - only GPL modules can use it

# Fix: remove use of GPL-only symbol, OR license module as GPL
# Cannot: just ignore the restriction (kernel enforces it technically)
```

---

### Related Keywords

**Foundational:**
LNX-001 (Linux overview), LNX-109 (Torvalds history)

**Builds on this:**
LNX-111 (kernel architecture), LNX-112 (kernel development process)

**Related:**
LNX-111 (kernel architecture), LNX-112 (development), LNX-113 (eBPF future)

---

### Quick Reference Card

| License | Copyleft? | Can link from proprietary? | Key use |
|---------|-----------|--------------------------|---------|
| GPL v2 | Strong | No | Linux kernel, GCC |
| GPL v3 | Strong + patents + Tivo | No | Many GNU tools |
| LGPL v2.1 | Weak (library only) | Yes (dynamic) | glibc, Qt |
| AGPL v3 | Network copyleft | No | Server-side services |
| MIT | None | Yes | React, Node.js |
| Apache 2.0 | None | Yes (+ patent grant) | Kubernetes, Android |
| BSD 2/3 | None | Yes | OpenBSD, FreeBSD |

**3 things to remember:**
1. GNU tools (GCC, bash, coreutils, glibc) existed BEFORE Linux. Linux provided the missing kernel. GNU + Linux kernel = complete free OS. Stallman calls it GNU/Linux; Torvalds and most people call it Linux.
2. GPL copyleft: "share-alike" - derivative works must also be GPL. Triggered when you DISTRIBUTE GPL software (not when you use it internally). LGPL is weaker: can link LGPL libraries into proprietary software (with conditions).
3. Android is GPL v2 kernel + Apache user space: legal because Linux kernel and Android apps are separate programs communicating via system calls, not linked together. Bionic (Android's custom libc) is Apache 2.0, breaking the LGPL glibc chain.

---

### Transferable Wisdom

GPL's copyleft mechanism transfers to: Creative Commons Share-Alike (CC-BY-SA)
for creative works (Wikipedia license), Open Database License (ODbL) for
datasets (OpenStreetMap), SIL Open Font License for fonts (Linux's default
fonts). The "viral" copyleft concept is applied in: patent pools (FRAND,
essential patents must be licensed reasonably), W3C web standards (patent
royalty-free commitments), RISC-V ISA (open standard with royalty-free use).
The four freedoms philosophy maps to: open-access academic publishing (right to
read and redistribute research), open hardware (OSHWA definition, similar to
four freedoms for hardware designs), Right to Repair movement (freedom to study
and modify your own physical devices). The dual licensing model (GPL + commercial)
is used by: MySQL (Oracle), Qt (Qt Company), Redis (BSL), MongoDB (SSPL) - the
evolution from pure GPL toward "open core" or "source available" models shows the
commercial tension with copyleft. Understanding GPL compatibility is the same
cognitive challenge as: type system compatibility in programming languages
(can you pass X where Y is expected?), network protocol compatibility (can protocol
A speak to protocol B?), API versioning (can client using v1 speak to server using v2?).
The OSI/FSF naming dispute illustrates: how the same technology can be framed
differently for different audiences (technical merit vs. ethical framework),
a pattern seen in: climate discussion (economic impact vs. moral obligation),
AI regulation (innovation vs. safety), data privacy (utility vs. rights).

---

### The Surprising Truth

The GNU Project was announced in 1983. GNU Hurd (the kernel Stallman intended
to use) was started in 1990. In 2024, GNU Hurd is still not production-ready.
It has been "almost ready" since approximately 1995. The most widely deployed
operating system in history (GNU/Linux, via Android, cloud servers, supercomputers)
uses a kernel that Stallman did NOT write and initially didn't plan to use.

The deeper irony: the tools Stallman designed (GCC, glibc, bash) are what
made Linux practically possible. Without GCC, Torvalds could not have compiled
the Linux kernel. Without bash, Linux would have had no shell. The GNU tools
and the GPL license were the infrastructure that Linux needed but didn't have
to build. Stallman's decade of work on GNU tools was necessary for Linux to
succeed - yet Stallman's own kernel project (Hurd) failed to take advantage of
the opportunity he created. History's most consequential "forgotten contribution":
Stallman built the foundation that Linux stood on, while receiving insufficient
credit for it (even from Torvalds), and his own OS project never shipped.

---

### Mastery Checklist

- [ ] Can name the four GNU freedoms and what each means practically
- [ ] Understands how copyleft works and when GPL is "triggered" (distribution, not use)
- [ ] Knows the key GPL variants: GPL v2 vs v3, LGPL, AGPL, and when each is appropriate
- [ ] Can explain why Android can have proprietary apps despite using the GPL v2 Linux kernel
- [ ] Understands the free software vs open source distinction (philosophy vs pragmatism)

---

### Think About This

1. MongoDB switched from AGPL to SSPL (Server Side Public License) in 2018,
   saying that cloud providers (AWS DocumentDB) were offering MongoDB as a
   service without contributing back. Is SSPL a valid evolution of copyleft,
   or is it fundamentally different? What is the purpose of copyleft (ensuring
   improvements flow back to the community) and does SSPL achieve it? How
   does SSPL's requirement (if you offer the software as a service, open-source
   your entire service) compare to AGPL's requirement (open-source the code
   you run as a service)? What incentive structure does each create for cloud
   providers?

2. An engineer argues: "Permissive licenses (MIT, Apache) have won. Look at
   Kubernetes (Apache 2.0), Docker (Apache 2.0), TensorFlow (Apache 2.0),
   React (MIT), Node.js (MIT). All the modern infrastructure is permissive,
   not copyleft." Is this observation accurate? What explains the shift from
   GPL-dominated open source (Linux, GCC, Git) to Apache/MIT-dominated cloud
   native tooling? Does this represent a defeat for the free software movement
   or a maturation of open-source strategy? What would Stallman say vs what
   would Raymond say?

3. The EU Cyber Resilience Act (2024) may require: software placed on the EU
   market to have no known unpatched vulnerabilities, security updates for
   the supported lifetime. This would affect open-source maintainers: an
   individual who maintains a library on GitHub and accepts no money could
   be legally liable for security vulnerabilities under the CRA. How should
   open-source licensing evolve to address regulatory pressure? Does GPL
   provide any protection (it includes a disclaimer of warranty)? What does
   this mean for the sustainable funding of open-source infrastructure?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between GPL and MIT licenses, and when would you use each for a project?
A: CORE DIFFERENCE - COPYLEFT VS PERMISSIVE: MIT is a permissive license: grants all four software freedoms, PLUS allows recipients to distribute under different terms (including proprietary). Key phrase: "provided that the above copyright notice and this permission notice appear in all copies." That's it. No copyleft. GPL (v2 or v3) is a copyleft license: grants all four software freedoms, BUT requires: any distributed derivative work must also be GPL, source code must be available. The "copyleft" or "viral" property: takes copyright law normally used to restrict software and inverts it to ensure software remains free. PRACTICAL IMPLICATIONS: MIT project: company X can take your MIT library, add proprietary features, ship binary-only, compete with you, owe you nothing except attribution. This happened: Apple uses MIT/BSD code throughout macOS, keeping proprietary modifications private. GPL project: company X can take your GPL library, add features, but MUST release those features under GPL. IBM contributed SMP support to Linux (GPL) - had to release code. This improved Linux for everyone. WHEN TO USE EACH: Use MIT/Apache when: (1) You want maximum adoption (companies won't use GPL libraries in proprietary products), (2) The project is a tool/library and you care more about wide use than ensuring improvements return, (3) You want the project to be the foundation of a commercial ecosystem (React, Kubernetes, Docker), (4) Corporate contributions are desirable. Use GPL when: (1) You want to ensure derivative works remain free, (2) You're competing with commercial alternatives and need them to contribute back, (3) Your project is a complete application (not a library), (4) You're willing to accept reduced corporate adoption in exchange for copyleft guarantees. SPECIAL CASES: LGPL for libraries where you want permissive use but modifications to the library itself to be shared. AGPL for web services where you want service providers to share their modifications (prevents SaaS black-box forks). Dual licensing (GPL + commercial) for commercial sustainability: users choose: either comply with GPL or pay for a commercial license.

**Expert:**
Q: Explain the GPL v2 vs GPL v3 differences and why the Linux kernel is GPL v2 only.
A: THREE KEY GPL V3 CHANGES AND WHY TORVALDS REFUSED: (1) TIVOIZATION CLAUSE (Section 6): GPL v3 requires that if you distribute GPL software in hardware products, users must be able to run MODIFIED VERSIONS on that hardware. If hardware uses cryptographic keys to prevent modified software from running (like TiVo did with Linux), GPL v3 is violated. Torvalds's argument: "I don't believe that hardware manufacturers have an obligation to allow me to run my modified kernel on their hardware. I believe in freedom to USE software (run, modify, study), not freedom to run modified versions on arbitrary hardware." Stallman's argument: "Without this freedom, the right to modify is hollow - you can modify but not run your modifications on the hardware you own." (2) PATENT RETALIATION CLAUSE (Section 11): GPL v3 explicitly grants a patent license for the software, and revokes it if the licensee initiates patent litigation against the licensor. Torvalds: Linux predates many software patents; adding patent clauses creates new legal complexity and uncertainty. Many kernel contributors hold patents; this clause creates unclear interactions. (3) ADDITIONAL PERMISSIONS MECHANISM (Section 7): GPL v3 allows extra permissions that can be added to create other compatible licenses (creating a permission-granting framework). This adds complexity. THE "GPL v2 ONLY" CHOICE: Torvalds explicitly chose "GPL v2 only" (not "v2 or later"). "GPL v2 or later" code CAN be combined with GPL v3 code (both grant permission to use v3). "GPL v2 only" code CANNOT be combined with GPL v3 code (because v3 has additional restrictions from v2's perspective - the Tivoization clause is an "additional restriction"). Result: Linux kernel (GPL v2 only) cannot incorporate GPL v3-licensed code. Some kernel contributors have expressed interest in moving to GPL v2 or later, but Torvalds's position has kept it at v2 only. PRACTICAL CONSEQUENCE: Many GNU tools are "GPL v3 or later" (GCC, bash, gdb). Linux is "GPL v2 only." This creates a legal boundary between the kernel (v2) and GNU user-space tools (v3) - which is fine because they are separate programs (kernel and user space communicate via system calls, not by linking together).
