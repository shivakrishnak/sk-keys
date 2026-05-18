---
id: LNX-112
title: "The Linux Kernel Development Process (LKML, Patches)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-109, LNX-111
used_by: LNX-113, LNX-114
related: LNX-109, LNX-111, LNX-113, LNX-114
tags: [kernel-development, lkml, linux-mailing-list, patch-submission, merge-window, release-cycle, maintainers, greg-kroah-hartman, ingo-molnar, torvalds, git-send-email, format-patch, checkpatch, signed-off-by, stable-kernel, lts-kernel, rc-releases, subsystem-trees, linux-next, kernel-workflow, open-source-governance, kernel-newbies, staging-drivers, coverity, sparse, coccinelle, kconfig]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 112
permalink: /technical-mastery/lnx/linux-kernel-development-process-lkml-patches/
---

## TL;DR

The Linux kernel follows a **strict email-based development process** centered
on the **LKML (Linux Kernel Mailing List)**. Development cycle: Linus opens
a **2-week merge window** (subsystem trees merged into mainline), then 8 weeks
of **-rc releases** (rc1 through rc7/8: bug-fix only), then stable release.
Cadence: new version every **9-10 weeks**. Architecture: Torvalds at top,
~100 **subsystem maintainers** as trusted lieutenants (Greg Kroah-Hartman for
stable/drivers, Ingo Molnar for scheduler, David Miller for networking).
Patch submission: `git format-patch` + `git send-email` -> LKML review ->
revisions (v2, v3...) -> subsystem maintainer `Reviewed-by:` / `Acked-by:`
-> Linus merge during next window. Every patch needs **`Signed-off-by:`**
(Developer Certificate of Origin: DCO). `scripts/checkpatch.pl`: style
checker, must pass. `linux-stable` tree: backports of critical fixes to
older kernels. **LTS (Long-Term Support)** kernels (e.g., 5.15, 6.1) maintained
for 2-6 years - chosen by kernel.org admins, used in production infrastructure.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-112 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | LKML, patch submission, merge window, LTS, stable kernel, maintainers, DCO, checkpatch |
| **Prerequisites** | LNX-109 (Torvalds history), LNX-111 (kernel architecture) |

---

### The Problem This Solves

**Scale challenge**: 15,000+ active contributors, 2000+ changes per release,
a 30-million-line codebase. How do you coordinate global contribution without
bureaucratic bottlenecks? The LKML-based model: email is asynchronous (works
across time zones), searchable (archive available at lore.kernel.org), transparent
(public record of all decisions), reviewer-identified (commit messages record
who reviewed and approved each change).

**Quality challenge**: A kernel bug can crash millions of servers simultaneously.
How do you ensure patches are correct before they reach production? Multi-stage
review (LKML discussion -> subsystem maintainer ack -> linux-next testing ->
rc release testing -> stable release) with each stage adding confidence.

---

### Textbook Definition

**LKML (Linux Kernel Mailing List)**: The primary communication channel for
Linux kernel development. Public mailing list where patches are submitted,
reviewed, discussed, and decisions are made. Archive: lore.kernel.org.

**Merge window**: The ~2-week period at the start of each kernel development
cycle when subsystem trees are merged into Linus's mainline tree. Only work
already staged in subsystem trees (e.g., `net-next`, `mm`) is eligible.

**Subsystem maintainer**: A trusted individual responsible for a specific
kernel subsystem (networking, scheduling, storage, etc.). Receives patches
for their subsystem, performs code review, and submits a pull request to
Linus during the merge window.

**LTS kernel**: A specific stable kernel version selected for long-term
maintenance (2-6 years). Selected from stable releases by kernel.org admins
based on expected deployment demand. Receives only critical bug fixes and
security patches.

---

### Understand It in 30 Seconds

```bash
# === Linux kernel release schedule ===

# Check current mainline kernel versions:
# (from kernel.org)
# 6.9      (mainline: latest development)
# 6.8.x    (stable: bug-fix updates)
# 6.6.x    (longterm/LTS: until Dec 2026)
# 6.1.x    (longterm/LTS: until Dec 2026)
# 5.15.x   (longterm/LTS: until Dec 2026)
# 5.10.x   (longterm/LTS: until Dec 2026)
# 5.4.x    (longterm/LTS: until Dec 2025)

# Development timeline for a typical kernel (e.g., 6.9):
# Week 0:   Linus releases 6.8 stable
#           Merge window OPENS (2 weeks)
# Week 0-2: Maintainers submit pull requests from subsystem trees
#           Linus merges ~10,000-12,000 commits during merge window
# Week 2:   Merge window CLOSES, 6.9-rc1 released
# Week 3:   6.9-rc2 (only bug fixes now, no new features)
# ...
# Week 9:   6.9-rc7 or rc8 released
# Week 10:  6.9 released (if stable enough, else more rcs)
# Total: 9-10 weeks per release

# See kernel version:
uname -r
# 6.1.0-21-amd64   <- Debian LTS kernel (based on 6.1 LTS)
# 6.8.0-40-generic <- Ubuntu mainline kernel

# Check if running LTS or stable:
cat /proc/version_signature 2>/dev/null  # Debian-specific
# Ubuntu 6.8.0-40.40 ... (Ubuntu's build number)

# === Patch submission workflow ===

# Step 1: Clone kernel source:
git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
# (or: git.kernel.org/torvalds/linux)

# Step 2: Make your change:
# Edit files, add feature or fix bug

# Step 3: Commit with proper format:
git commit -s  # -s adds Signed-off-by automatically
# Commit message format (STRICT):
# Subject: subsystem: component: brief description (max ~72 chars)
# (blank line)
# Problem description: what was wrong or missing
# (blank line) 
# Solution description: how the patch fixes it
# (blank line)
# Signed-off-by: Your Name <email@example.com>
# Reviewed-by: Reviewer Name <reviewer@example.com>
# Acked-by: Maintainer Name <maintainer@example.com>
# Fixes: abc123def456 ("subsystem: original buggy commit")
# Cc: stable@vger.kernel.org  # if fix should go to stable kernels

# Step 4: Run checkpatch:
scripts/checkpatch.pl --strict -g HEAD~..HEAD
# Checks: line length, whitespace, C style, Signed-off-by presence
# Must pass before submitting (reviewers will ask you to fix if you don't)

# Step 5: Find maintainer(s) to CC:
scripts/get_maintainer.pl --patch 0001-my-fix.patch
# Outputs: maintainers and mailing lists for affected files
# Always CC all of them

# Step 6: Format patches:
git format-patch -1 HEAD         # single patch
git format-patch HEAD~3..HEAD    # last 3 patches as a series
# Creates: 0001-subsystem-component-brief.patch
# For series: 0001, 0002, 0003 + optional 0000 cover letter

# Step 7: Send via email:
git send-email \
  --to=maintainer@kernel.org \
  --cc=linux-kernel@vger.kernel.org \
  --cc=relevant-subsystem-list@vger.kernel.org \
  0001-my-fix.patch

# Step 8: Wait for review
# Reviewers may reply on LKML with:
# "Reviewed-by: X" -> positive review
# "Acked-by: X" -> ack from affected maintainer
# "Tested-by: X" -> testd and works
# Or: questions, style requests, design concerns

# Step 9: Revise if needed
# Subject: [PATCH v2] subsystem: my fix description
# Address all reviewer concerns, add their tags if received
```

---

### First Principles

```
THE LINUX DEVELOPMENT HIERARCHY:

Level 0: Linus Torvalds
  Maintains: mainline/master tree (torvalds/linux on kernel.org)
  His role: final decision maker on architecture
             merges from subsystem trees during merge window
             occasional direct review for controversial patches
  Communication: lkml, occasional posts (famous for blunt criticism)

Level 1: Senior/Core Maintainers
  Greg Kroah-Hartman: linux-stable, USB, drivers/staging, driver core
  Ingo Molnar: x86, scheduler (CFS), kernel locking, tracing
  David Miller (until 2022 retirement): networking (net/next)
  Jakub Kicinski: networking (after Miller)
  Theodore Ts'o: ext4, random, file systems
  Al Viro: VFS, many filesystems  
  Mauro Carvalho Chehab: media subsystem (DVB, V4L2)
  Arnd Bergmann: ARM architecture
  
  Each maintains their own git tree (e.g., "net-next" for networking)
  Merges patches from their area, submits pull request to Linus
  during merge window

Level 2: Subsystem Maintainers
  Each major driver, protocol, architecture has a maintainer
  Listed in: MAINTAINERS file (30,000+ lines!)
  
  How to find who to send a patch to:
  scripts/get_maintainer.pl drivers/net/ethernet/intel/igb/igb_main.c
  # Intel networking team + Jakub Kicinski (net) + networking list

Level 3: Contributors
  Anyone can send patches to LKML
  First contribution: often a staging driver cleanup
  Most active contributors: Red Hat, Intel, Google, Samsung, IBM, ARM

THE DUAL GIT TREE SYSTEM:

For each major subsystem, there are typically TWO trees:
  - "xxx" tree: current stable, receives only bug fixes
  - "xxx-next" tree: next merge window features

Example (networking):
  "net" (Jakub Kicinski): only bug fixes for current -rc cycle
  "net-next" (same): new features, queued for next merge window

During merge window: Linus merges "net-next" 
During -rc phase: only "net" (bug fixes) can go to mainline

Why two trees:
  Prevents mixing new features with regression fixes
  "net-next" can have experimental work without destabilizing -rc
  Clear policy: no new features after rc1

THE STABLE KERNEL SYSTEM:

greg@kroah.com leads linux-stable@vger.kernel.org
  
What gets backported to stable:
  "Important bug fixes" (not features!)
  Must have Cc: stable@vger.kernel.org in commit (or via review)
  Or: patches can be nominated after the fact via email to stable
  
Backport criteria (Documentation/process/stable-kernel-rules.rst):
  1. Fix a real bug that causes real problems
  2. Not introduce new bugs
  3. Be obviously correct
  4. Be small enough to verify
  5. Already in mainline or a later stable release

LTS selection:
  Not formally announced in advance
  Greg Kroah-Hartman decides based on community interest
  Typically: one kernel per year designated LTS
  Recent LTS kernels: 4.14, 4.19, 5.4, 5.10, 5.15, 6.1, 6.6
  EOL: check kernel.org/releases.json

WHY EMAIL-BASED DEVELOPMENT (vs GitHub PRs)?

1. Email works at any scale: 1,000 patches/week without GitHub going down
2. Asynchronous: Torvalds in Portland, Molnar in Budapest, Kroah-Hartman at IBM
3. Searchable archive: git blame + lore.kernel.org = why a commit was made
4. Flat discussion: no single company controls the "platform"
5. Patch text is code: email preserves exact diff, no platform reformatting

Critique:
  - Higher barrier to entry than PRs (git send-email setup is painful)
  - Review tools (b4, patchwork) improve UX but email remains primary
  - Some maintainers use GitHub mirrors with experimental PR workflows
  - kernel.org has Patchwork (tracks patch state: new/accepted/rejected)
  
Recent evolution:
  b4 tool: simplifies LKML patch handling
  lore.kernel.org: modern LKML archive with threading
  GitHub kernel mirror: read-only for discoverability
```

---

### Thought Experiment

Submitting a real kernel bug fix:

```bash
# === Real-world patch submission walkthrough ===

# Scenario: you find that a USB device driver has a memory leak.
# The driver allocates a buffer in probe() but doesn't free it in disconnect()

# Step 1: Set up for contribution:
git config --global user.email "developer@example.com"
git config --global user.name "First Last"
# git send-email needs smtp config (or use local postfix/sendmail)
# Many contributors: use smtp.gmail.com or employer SMTP

# Step 2: Find the file and understand the bug:
# drivers/usb/serial/cp210x.c
# cp210x_port_probe() allocates priv = kzalloc(...)
# cp210x_port_remove() is missing kfree(priv)

# Step 3: Make the fix:
# (edit the file)
git diff
# --- a/drivers/usb/serial/cp210x.c
# +++ b/drivers/usb/serial/cp210x.c
# @@ -450,6 +450,7 @@ static int cp210x_port_remove(struct usb_serial_port *port)
#  {
#         struct cp210x_port_private *port_priv = usb_get_serial_port_data(port);
# +       kfree(port_priv);
#         return 0;
#  }

# Step 4: Write the commit message correctly:
git add drivers/usb/serial/cp210x.c
git commit
# (opens editor - write:)
# USB: serial: cp210x: fix memory leak in port_remove
#
# The cp210x_port_probe() function allocates a cp210x_port_private
# struct but cp210x_port_remove() does not free it, causing a memory
# leak when the device is disconnected.
#
# Free the port_private struct in the remove function to fix the leak.
#
# Fixes: abc12345 ("USB: serial: cp210x: add port private data")
# Cc: stable@vger.kernel.org
# Signed-off-by: First Last <developer@example.com>

# Step 5: Run checkpatch:
scripts/checkpatch.pl --strict -g HEAD~..HEAD
# If OK: "total: 0 errors, 0 warnings, 0 checks, 10 lines checked"
# If not OK: fix issues and amend commit

# Step 6: Find maintainers:
scripts/get_maintainer.pl -f drivers/usb/serial/cp210x.c
# Johan Hovold <johan@kernel.org> (maintainer)
# linux-usb@vger.kernel.org (mailing list)
# linux-kernel@vger.kernel.org (broad CC)
# Greg Kroah-Hartman <gregkh@linuxfoundation.org> (USB subsystem)

# Step 7: Create patch:
git format-patch -1 HEAD
# 0001-USB-serial-cp210x-fix-memory-leak-in-port_remove.patch

# Step 8: Send:
git send-email \
  --to="Johan Hovold <johan@kernel.org>" \
  --cc="linux-usb@vger.kernel.org" \
  --cc="linux-kernel@vger.kernel.org" \
  --cc="stable@vger.kernel.org" \
  0001-USB-serial-cp210x-fix-memory-leak-in-port_remove.patch

# Step 9: Wait for review
# Likely response within 1-2 weeks from Johan Hovold
# Johan might say: "Reviewed-by: Johan Hovold <johan@kernel.org>"
# Or: "Can you also check cp210x_open() for similar issues?"
# Revise: git commit --amend, git format-patch, send v2

# Step 10: Patch acceptance
# After approval: Johan adds to his USB tree
# Next merge window: merged into mainline
# Stable kernel: because of Cc: stable@vger.kernel.org
#   Greg backports it to 6.1.y, 5.15.y, 5.10.y etc.
#   Your fix protects users on older kernels too!

# === How to find your first contribution ===

# kernelnewbies.org: good first bugs
# Documentation/process/howto.rst: official guide

# Staging drivers: drivers needing cleanup (checkpatch warnings OK to fix)
ls drivers/staging/
# greybus/  iio/  media/  ...
# Pick a driver, fix a checkpatch warning:
find drivers/staging/ -name "*.c" | \
  xargs scripts/checkpatch.pl 2>&1 | grep "WARNING:" | head -20
# WARNING: Use of volatile is usually wrong
# -> fix: often just remove `volatile` keyword that's unnecessary
```

---

### Mental Model / Analogy

```
The Linux development process = peer-reviewed academic journals

Academic journal:       | Linux kernel development:
------------------------|---------------------------------
Journal (Nature/PLDI)   | LKML + subsystem mailing lists
Editor-in-chief         | Linus Torvalds
Associate editors       | Subsystem maintainers  
Peer reviewers          | LKML community
Paper submission        | git format-patch + git send-email
Review comments         | Reply-to-patch on LKML
Revision (R1, R2...)    | PATCH v2, v3...
"Accept" decision       | Maintainer merge into subsystem tree
Publication             | Linus merge into mainline during merge window
Errata/corrections      | Stable kernel backports
Archive                 | lore.kernel.org (searchable forever)
Citation                | git blame (why was this change made?)
Impact factor           | How many systems run this code?

Both systems share:
- Public peer review (anyone can review a patch, comment on LKML)
- Formal provenance (Signed-off-by = author certification, like authorship)
- Iterative revision (v2, v3 patches = R1, R2 revisions)
- Domain experts as reviewers (VFS maintainer reviews VFS patches)
- Permanent archive of reasoning (email thread = design rationale)
- High bar for inclusion (quality over quantity)

Differences from GitHub PRs:
GitHub PR:              | LKML patch:
------------------------|---------------------------------
Web UI, button merge    | Email, command-line
Per-commit history lost | Commit message preserved forever
Format not controlled   | Strict format (checkpatch enforced)
No legal certification  | Signed-off-by (DCO legal)
Platform-dependent      | Universal (works on any email client)
Easy to spam            | Barrier to entry filters quality

The Signed-off-by line:
Developer Certificate of Origin (DCO):
  By adding "Signed-off-by: Name <email>", you certify that:
  a) You wrote it (original work)
  b) You have rights to contribute it (not under NDA/IP conflict)
  c) The project can distribute it under the specified license
  d) You understand this is permanent and public
  
  This is what lawyers call an "attestation."
  It's the reason Linux contributions are legally defensible:
  Unlike some projects with contributor license agreements (CLAs),
  Linux uses DCO: lightweight, per-commit, legally sound.
  
  SCO lawsuit (2003): SCO claimed Linux contained their copyrighted code
  DCO/commit history: kernel was able to trace provenance of every line
  Result: SCO's claims were debunked line by line (Groklaw analysis)
```

---

### Gradual Depth - Five Levels

**Level 1:**
How to check which kernel version you're running. What LKML is. The merge
window concept. Why Linux has version numbers like 6.1.0. How to find a
kernel bug fix for your version. What LTS kernels are.

**Level 2:**
The two-week merge window timeline. -rc releases and what they mean. Subsystem
trees concept. greg@ stable kernel backport process. Signed-off-by and DCO.
checkpatch.pl usage. How to find the maintainer for a file. lore.kernel.org archive.

**Level 3:**
Full patch submission workflow: format-patch, send-email, revision cycle.
How `linux-next` integration tree works (aggregates subsystem trees, tests
integration before merge window). How the staging tree (drivers/staging/) works
as an incubation area. Kernel CI (continuous integration): kernelci.org,
Intel 0Day testing, Google syzbot (kernel fuzzer finding bugs 24/7). How
to add a Cc: stable@vger.kernel.org tag and why.

**Level 4:**
The MAINTAINERS file format: F: patterns, M: maintainers, L: lists, S: status.
How to navigate patch series with cover letters. How to handle conflicts in
linux-next. The "linux-firmware" repository and how it differs from the kernel.
How bisect (git bisect) integrates with kernel bug reports. The role of
checkpatch's --strict vs default mode. How syzbot reports and tracks kernel bugs.

**Level 5:**
The GPL compliance tracking in kernel commits (SPDX-License-Identifier per file).
How the kernel Git history represents a legal record of provenance. The controversy
around GitHub Copilot and kernel copyright (Copilot trained on GPL code, generating
non-GPL code). The "Contributor" vs "author" distinction in kernel commits (git blame
vs git log --follow). How LTS selection and maintenance affects the embedded and
enterprise Linux ecosystem. The kernel's relationship to SystemD controversy
(not a kernel issue, but illustrates community governance dynamics).

---

### Code Example

```bash
# === Good patch series with cover letter (multi-patch example) ===

# BAD: send 5 related fixes as one giant patch
# Harder to review, harder to bisect, harder to backport individual fixes

git log --oneline HEAD~5..HEAD
# abc1234 mm: memcg: fix charge overflow in multiple places
# (single commit combining 5 different fixes - BAD!)

# GOOD: each logical fix as a separate patch, with cover letter
git log --oneline HEAD~5..HEAD
# def1234 mm: memcg: fix overflow in charged_bytes calculation  
# def5678 mm: memcg: fix race in memcg_charge_kmem()
# def9012 mm: memcg: add lockdep assertion for charge path
# def3456 mm: memcg: add overflow check in mem_cgroup_do_precharge
# def7890 mm: memcg: fix error handling in charge_memcg_tree()
# Each patch: single logical change, easy to review independently
# If one is wrong: others still apply

# Generate series with cover letter:
git format-patch --cover-letter -5 HEAD
# 0000-cover-letter.patch
# 0001-mm-memcg-fix-overflow-in-charged_bytes-calculation.patch
# 0002-mm-memcg-fix-race-in-memcg_charge_kmem.patch
# ...

# Edit 0000 cover letter:
# Subject: [PATCH 0/5] mm: memcg: fix multiple overflow and race conditions
# (blank line)
# This series fixes five related issues in the memory cgroup charge path:
# ... (overall description of the series)
# Signed-off-by: ...

# === checkpatch.pl common issues ===

# Run checkpatch on your patch BEFORE sending:
scripts/checkpatch.pl --strict 0001-my-fix.patch

# Common failures:
# ERROR: code indent should use tabs where possible
#   -> Replace spaces with tabs (kernel uses tab=8 spaces, not 4)
# WARNING: line over 80 characters
#   -> Break long lines (strict: 80; recommended: <=80)
# WARNING: Missing a blank line after declarations
#   -> Add blank line between variable declarations and code
# ERROR: do not use EXPORT_SYMBOL_GPL for xxx
#   -> Don't export GPL symbols from non-GPL code
# WARNING: Prefer kernel type 'u32' over 'uint32_t'
#   -> Use kernel-specific types (s8, u8, s16, u16, s32, u32, s64, u64)
# ERROR: Missing Signed-off-by: line
#   -> Required! Add with: git commit -s or manually

# === Checking a patch in the LKML archive ===

# Find if a bug fix is in your kernel:
# 1. Find the commit hash from kernel commit log or bugzilla
# Example: CVE-2023-1234 fixed in commit ab12cd34

# 2. Check if it's in your running kernel:
git log --oneline v6.1..HEAD 2>/dev/null | grep ab12cd34
# Or: check if version number contains the fix
# Ubuntu: apt-cache show linux-image-$(uname -r) | grep Changelog

# 3. Check the stable tracking:
# Visit: https://lore.kernel.org/stable/
# Or: patchwork.kernel.org/project/stable-regressions
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "The kernel development process is chaotic and uncontrolled" | The Linux development process is rigorously structured - more so than most corporate development. Every patch has: a clear author (Signed-off-by), a clear reviewer (Reviewed-by/Acked-by), an approval chain (subsystem maintainer -> Linus), a test period (-rc releases), and a permanent searchable archive (lore.kernel.org). The process produces 70,000-80,000 commits per year across 15,000+ contributors with fewer regressions per line than most proprietary OS kernels. The appearance of chaos comes from: (1) it's done via email (unfamiliar to PR-based developers), (2) review is public and sometimes blunt (Torvalds's famous harsh feedback emails), (3) there's no central ticketing system (discussion is in email threads). But the outcome is: a kernel version released every 9-10 weeks with LTS support for 2-6 years - a very predictable process by any measure. |
| "Linus Torvalds personally reviews all 70,000+ commits per year" | Linus reviews only a tiny fraction directly. He relies on a trusted hierarchy of ~100 subsystem maintainers. Each maintains their own git tree (e.g., Greg Kroah-Hartman maintains linux-stable and drivers/usb, net/, etc.). These maintainers do detailed code review. Linus: merges pull requests from maintainers during the merge window (a pull request = "I reviewed all these patches, I trust them, please merge"). Linus typically reviews at the architectural level: design decisions, API choices, naming conventions - not individual bug fixes or driver changes. He focuses his energy on patches that change core architecture (memory management, scheduler, security). For large subsystems: Linus defers entirely to senior maintainers who he has trusted for years. This is why: Linux can handle 15,000+ contributors without Linus as a bottleneck. The system's scalability comes from delegated maintainership, not from Linus's personal review capacity. |
| "LTS kernels get all security fixes from newer kernels" | LTS kernels get SELECTED security fixes, not all of them. The backporting criteria is strict: the fix must be "obviously correct and minimal" for the older code path. A security fix in 6.5 may touch code that was completely rewritten in 5.15, making a direct backport impossible (different code structure, different code paths). In this case: the 5.15 version may get a different fix, a partial fix, or no fix if the vulnerability doesn't affect 5.15's code. Additionally: some vulnerabilities are only relevant to new hardware or features not present in older kernels. The Linux kernel community maintains separate CVE assignments via kernel.org/doc/html/latest/process/cve.html (as of 2024). Users of LTS kernels: should not assume 100% coverage of all CVEs. Enterprise distros (RHEL, SUSE) maintain more aggressive backporting policies than upstream LTS, which is part of why enterprise support subscriptions have value. |
| "You need to be an expert to contribute to the Linux kernel" | First contributions to Linux are often simple code style fixes. The kernel's staging/ directory (drivers/staging/) is explicitly maintained as an entry point for new contributors. Drivers in staging have known quality issues (listed in TODO files). Contribution examples: (1) Fix a checkpatch.pl warning (spaces vs tabs, long lines), (2) Remove unnecessary casts, (3) Fix a typo in a comment, (4) Add missing newline at end of file. These trivial patches still go through the full process (checkpatch, get_maintainer, send-email, review). The process is the learning, not the code complexity. After a few simple patches: contributing reviewers, bug reporters, test results (Tested-by). kernelnewbies.org documents all of this specifically for first-time contributors. The kernel has intentionally low initial barriers (trivial patches accepted) while maintaining high quality bars for critical code. |

---

### Failure Modes & Diagnosis

```bash
# === Common first-patch mistakes ===

# MISTAKE 1: Not running checkpatch first
git format-patch -1 HEAD
# Send to list without checking...
# Reviewer response: "Please fix all checkpatch errors first"
# Have to send v2 just for style issues

# Fix: ALWAYS run checkpatch before sending:
scripts/checkpatch.pl --strict -g HEAD~..HEAD
# Zero tolerance for errors

# MISTAKE 2: Including unrelated changes in the patch
# Your patch fixes a memory leak but also reformats the entire function

# Reviewer response: "Please separate the formatting from the fix"
# Fix: separate commits for fix vs cleanup
# Or: don't include cleanup unless the function is truly unreadable without it

# MISTAKE 3: Missing "Fixes:" tag for bug fixes
# If your patch fixes a regression introduced by a specific commit:
git log --oneline --follow -p -- drivers/usb/serial/cp210x.c | \
  grep "kzalloc" | head -5
# Find: which commit introduced the allocation you need to free

# Add to commit message:
# Fixes: abc12345 ("USB: serial: cp210x: add per-port private data")
# This allows: automated backport to stable kernels
# Without it: stable team may miss the fix

# MISTAKE 4: Not CCing the right people
# Use get_maintainer.pl:
scripts/get_maintainer.pl --patch 0001-my-fix.patch
# If you don't CC the right maintainer:
# Patch may be ignored (maintainer doesn't see it)
# Or: other maintainer replies "this isn't my tree, send to XYZ"

# MISTAKE 5: Sending HTML email (mail client issue)
# LKML strictly requires plain text patches
# Common culprit: Gmail web interface, Outlook
# Fix: use git send-email (handles encoding correctly)
# Or: use Mutt, Thunderbird with correct settings

# === Checking if a fix is in your kernel ===

# Method 1: Use git (if you have kernel source):
git log --oneline v5.15..v5.15.100 | grep "cp210x memory leak"

# Method 2: Check Debian changelogs:
apt-get changelog linux-image-$(uname -r) | grep -i "CVE-\|memory leak"

# Method 3: Check Ubuntu security notices:
# ubuntu.com/security/notices -> filter by kernel

# Method 4: Check kernel stable tracker:
# lore.kernel.org/stable -> search for commit hash
```

---

### Related Keywords

**Foundational:**
LNX-109 (Torvalds history), LNX-111 (kernel architecture)

**Builds on this:**
LNX-113 (eBPF future), LNX-114 (open problems)

**Related:**
LNX-113 (eBPF research), LNX-114 (open problems)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `uname -r` | Show current kernel version |
| `scripts/checkpatch.pl --strict` | Validate patch style |
| `scripts/get_maintainer.pl -f FILE` | Find patch recipient |
| `git format-patch -1 HEAD` | Create patch file |
| `git send-email PATCH` | Send patch to mailing list |
| `git commit -s` | Add Signed-off-by automatically |
| `lore.kernel.org` | Search LKML archive |
| `kernel.org/releases.json` | Check kernel EOL dates |

**3 things to remember:**
1. Two-week merge window -> 8 weeks of -rc bug fixes -> stable release. Every 9-10 weeks. Merge window: only subsystem tree pull requests (features pre-approved by maintainers). -rc phase: bug fixes only.
2. The maintainer hierarchy: subsystem maintainers (100+) -> Linus. Find via `scripts/get_maintainer.pl`. Every patch needs `Signed-off-by:` (DCO certification). `scripts/checkpatch.pl --strict` must pass before sending.
3. LTS kernels (5.10, 5.15, 6.1, 6.6) maintained 2-6 years, receive critical bug fixes and security patches only. Stable kernels: same, but 1 year. Enterprise distros (RHEL, SUSE): backport more aggressively than upstream LTS.

---

### Transferable Wisdom

The Linux patch review process mirrors: RFC (Request for Comments) process
for internet standards, where proposals are publicly discussed and iterated
before standardization. The DCO (Developer Certificate of Origin) is similar
to: commit signing in modern repositories (git commit -S with GPG key),
but lighter-weight (text-only, no crypto). The maintainer hierarchy is similar
to: Apache Software Foundation's PMC (Project Management Committee) structure,
where elected committers have merge authority. The staging tree as incubation
area is similar to: ASF incubator (new projects graduate from incubator to TLP),
CNCF sandbox/incubating/graduated stages for cloud-native projects. The "two
trees" pattern (feature tree + bugfix tree) is used in: Kubernetes (feature
freeze before release, only fixes after), many open-source projects with release
cycles, Red Hat's Fedora (Fedora = new features incubator for RHEL). The
`Fixes:` tag in kernel commits is similar to: GitHub `Closes #123` syntax
(cross-referencing the commit that introduced the bug), Jira link-to-issue,
CVE tracking in security advisories. The kernel's searchable email archive
(lore.kernel.org) is what many projects try to recreate in: GitHub Discussions,
Discourse forums, mailing list archives - understanding WHY a design decision
was made is as important as WHAT was decided.

---

### The Surprising Truth

The Linux kernel merge window produces approximately 10,000-12,000 commits in
two weeks. This means Linus Torvalds personally merges approximately 1 pull
request every 10 minutes, 24 hours a day, for 14 days straight. He does this
by reviewing and merging pull requests from ~100 subsystem maintainers, each
representing hundreds of reviewed-and-tested commits.

He famously complains about bad pull requests during this period: if a maintainer
submits a pull request without a good description of the changes, Torvalds will
ask for it to be redone. He once rejected a pull request from the ARM architecture
maintainers for having a merge commit that touched "arm" in 2010, triggering
his famous "I refuse to merge it" email.

The merge window is the most stressful period of the kernel development cycle,
yet it has executed reliably every 9-10 weeks for over 20 years - a software
logistics operation of remarkable consistency.

---

### Mastery Checklist

- [ ] Understands the 9-10 week Linux release cycle: merge window -> -rc phases -> stable
- [ ] Can submit a first kernel patch: commit format, checkpatch, get_maintainer, send-email
- [ ] Knows the difference between mainline, stable, LTS, and distribution kernels
- [ ] Understands the DCO (Signed-off-by) legal purpose
- [ ] Can find whether a security fix is included in a given kernel version

---

### Think About This

1. The Linux kernel development process has remained email-based for 30 years,
   while the rest of the software industry moved to GitHub pull requests. Is
   this conservatism (fear of change) or wisdom (a proven process that scales)?
   Compare the properties: GitHub PR reviews are more accessible (web UI) but
   create platform dependency. LKML patches are lower friction for automation
   but harder for newcomers. What would need to change about GitHub PRs to
   support 15,000 contributors and 70,000 commits/year without a monolithic
   company controlling the platform? Would moving to GitHub change who can
   contribute (would it increase diversity, or just change which demographics
   are comfortable)?

2. The "NEVER BREAK USERSPACE" rule means backward compatibility is maintained
   for decades. But the stable/LTS kernel system means security patches must
   be backported to code that may be 6 years old. This requires maintaining
   expertise in old code versions. Compare: the kernel's backporting approach
   to enterprise Java (LTS versions: 8, 11, 17, 21) or Python (EOL tracking),
   Android's Project Mainline (pushing kernel components to app-level for
   faster updates), and IoT firmware (often never updated at all). What is
   the right model for software that runs on billions of devices for years?
   How does the kernel community balance security (fast updates) vs stability
   (slow, careful changes)?

3. Syzbot (Google's kernel fuzzer, running 24/7 since 2017) has found over
   50,000 kernel bugs. Most are found within days of a kernel subsystem
   accepting new code. What does this say about code review's ability to
   catch bugs vs automated testing? If syzbot finds a bug in your submitted
   patch after it's merged: what is the correct process? How does the kernel
   handle the "regression" case (your fix for bug A introduces bug B)? How
   does this compare to continuous integration in application development?

---

### Interview Deep-Dive

**Foundational:**
Q: What is an LTS kernel and when would you choose it over the latest stable kernel?
A: LTS KERNEL DEFINITION: Long-Term Support kernel - a specific Linux kernel version maintained for 2-6 years (rather than the standard ~1 year for stable kernels). Maintained by Greg Kroah-Hartman's team. Receives: critical bug fixes and important security patches. Does NOT receive: new features, hardware support for new devices, API additions. Current LTS kernels (as of 2024): 5.4 (Dec 2025 EOL), 5.10 (Dec 2026 EOL), 5.15 (Dec 2026 EOL), 6.1 (Dec 2026 EOL), 6.6 (Dec 2026 EOL). Check: kernel.org/releases.json. WHEN TO USE LTS: (1) EMBEDDED/IoT systems: devices with 5+ year lifetimes that can't be reflashed frequently. Shipping a product in 2023 on kernel 6.1 LTS: supported until 2026, then you decide whether to invest in upgrading. (2) Enterprise Linux distributions: RHEL, SUSE, Ubuntu LTS base their kernels on upstream LTS, then add additional backports and patches. Choose RHEL 9 (kernel 5.14 base, RHEL backports until 2032) for production servers. (3) Production systems where stability > features: kernel upgrades are disruptive; LTS allows staying on same major version while getting security patches. WHEN TO USE LATEST STABLE: (1) Desktop systems: want latest hardware support, latest features. (2) Development environments: want latest kernel APIs for testing new code. (3) Cloud instances: provider controls kernel, typically uses recent stable. PRACTICAL GUIDANCE: Most production servers run distribution kernels (RHEL, Ubuntu LTS, Debian Stable) which are based on LTS but further patched by the distribution. For IoT/embedded: choose upstream LTS that aligns with device lifecycle. The distinction "LTS vs stable" matters most when you're building your own Linux system (OpenEmbedded/Yocto) rather than using a distribution. For standard server deployments: use your distribution's supported kernel, which will be LTS-based.

**Expert:**
Q: Walk through the complete lifecycle of a bug fix from report to reaching a production Ubuntu LTS server.
A: COMPLETE LIFECYCLE (a real security bug, e.g., a kernel memory leak): STEP 1 - DISCOVERY (Day 0): Syzbot (Google's 24/7 kernel fuzzer) finds a bug in drivers/net/wireless/. Reports: creates a bug report on syzkaller.appspot.com with reproducer code and kernel crash log. Or: a developer/researcher reports directly via LKML or security@kernel.org (for security-sensitive bugs). STEP 2 - FIX DEVELOPMENT (Day 1-7): The networking maintainer or driver author analyzes the report. Writes a fix. Internally sends to security@kernel.org if it's a security vulnerability (embargo until fix ready). For non-security: posts fix to LKML for review. STEP 3 - LKML REVIEW (Day 3-14): Community reviews on LKML. v2, v3 if revisions needed. Reviewer adds Reviewed-by. Maintainer adds to their tree (net or net-next depending on severity). STEP 4 - MAINLINE MERGE (varies): If critical (security/crash): can be fast-tracked into a -rc release. Normal: waits for next merge window (up to 10 weeks). Gets a commit hash in mainline (e.g., torvalds/linux commit abc12345). STEP 5 - STABLE BACKPORT (Day 1-30 after mainline): commit has "Cc: stable@vger.kernel.org" tag. Greg Kroah-Hartman's team picks it up automatically. Backported to: 6.8.y, 6.7.y (recent stable), 6.6.y, 6.1.y, 5.15.y, 5.10.y (LTS versions). Released as: 6.6.32, 6.1.91 etc. STEP 6 - DISTRIBUTION ADOPTION (Day 7-60): Ubuntu security team monitors stable releases and CVE databases. Patches the Ubuntu kernel package (ubuntu/linux.git). Tests: kernel team + automated testing. Releases: security update for Ubuntu 22.04 LTS (based on kernel 5.15). Users who have "unattended-upgrades" or run "apt upgrade": get patched kernel. After reboot: vulnerability fixed! STEP 7 - END USER: Production server running Ubuntu 22.04 LTS. `apt upgrade` pulls new linux-image package. After maintenance window reboot: `uname -r` shows new version (5.15.0-101-generic). `dmesg` shows no error (bug is fixed). Total timeline: security bug to most production servers: 2-8 weeks for critical security issues. Non-critical: 1-3 months.
