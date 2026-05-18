---
id: LNX-020
title: "Man Pages and Getting Help (man, --help, info)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-006
used_by: LNX-024
related: LNX-006, LNX-025, LNX-026
tags: [man, help, info, documentation, manual-pages, tldr, shell-help]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 20
permalink: /technical-mastery/lnx/man-pages-and-getting-help/
---

## TL;DR

Linux has comprehensive built-in documentation. `man command`
shows the full manual. `command --help` shows quick usage.
`man -k keyword` searches all manuals. Man pages are organized
in numbered sections: section 1 = commands, section 2 = system
calls, section 3 = C library functions. Mastering man pages
makes you self-sufficient on any Linux system without internet
access - critical for production server work.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-020 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | man, --help, info, documentation, man sections, apropos |
| **Prerequisites** | LNX-006 |

---

### The Problem This Solves

On a production server at 3am, with no internet access, you need to
know an obscure flag for `find` or what a specific /proc file contains.
Linux's man pages provide comprehensive, authoritative documentation
for every command, system call, and library function - directly on
the system, always available, always accurate for that system's
installed version.

---

### Textbook Definition

**Man pages** (manual pages) are the traditional Unix/Linux documentation
system. Each page describes a single command, system call, library
function, or configuration file. They follow a standard format with
sections: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXAMPLES, SEE ALSO.

Man pages are organized in numbered sections:
1. User commands
2. System calls (kernel interface)
3. C library functions
4. Device files
5. File formats and conventions (/etc/passwd, etc.)
6. Games
7. Miscellaneous (protocols, conventions)
8. System administration commands

`info` pages: GNU project's alternative documentation system (more
hyperlinked, more detailed for GNU tools).

---

### Understand It in 30 Seconds

```bash
# View the manual for a command:
man ls                  # manual for ls command
man -k "list files"     # search manuals for phrase (also: apropos)
man 2 open              # section 2: the open() system call
man 5 crontab           # section 5: crontab file FORMAT (not command)
man 1 crontab           # section 1: crontab COMMAND

# Quick help (shorter than man):
ls --help               # brief usage summary
grep --help
find --help | less      # pipe to less if long

# Navigate inside man (it uses less):
q         = quit
SPACE     = page down
/pattern  = search forward
n         = next match
g         = go to beginning
G         = go to end

# Search for man pages by keyword:
man -k network           # same as: apropos network
man -k "file descriptor"

# Find which man page to read:
whatis ls               # one-line description
whatis crontab          # shows: crontab (1) and crontab (5)
```

---

### First Principles

**Why man pages exist on the system (not just the internet):**
Man pages are installed with each package. When you install nginx, you
also get `man nginx`. The man page matches exactly the version installed.
This is critical: `man nginx` shows the features available on THIS system's
version. Online documentation might show a newer or older version.

**Man section disambiguation:**
Some topics have multiple man pages in different sections:
- `man crontab` = section 1: the `crontab` command (how to use it)
- `man 5 crontab` = section 5: the crontab file FORMAT (the syntax)
- `man printf` = section 1: the `printf` shell command
- `man 3 printf` = section 3: the C library `printf()` function

When you see a cross-reference like `crontab(5)` in documentation,
the number is the section. `man 5 crontab` reads that specific page.

---

### Thought Experiment

You need to archive a directory, including hidden files, preserving
permissions, and excluding .git directories. You know `tar` is the tool
but don't remember the flags.

Without man pages: search the internet, find 5 conflicting Stack Overflow
answers, guess at the right combination.

With man pages:
```bash
man tar
# Press / to search
/--exclude    # find the --exclude flag: "tar --exclude=PATTERN"
/--preserve   # find preservation options
/--hidden     # or search for hidden file behavior

# Now construct:
tar --exclude='.git' -czf archive.tar.gz ./directory/
```

Man pages: authoritative, version-matched, available offline, and
contain cross-references (SEE ALSO) to related commands.

---

### Mental Model / Analogy

Man pages are like **instruction manuals stored in the appliance itself:**

```
Your washing machine = Linux command (tar, grep, sed)
  
Internet search = trying to find the manual on a third-party website
  (might be for a different model, might be outdated, might be wrong)
  
man tar = opening the manual stored INSIDE the machine
  (always matches your exact model, always complete, always accurate)
  
--help = the quick-reference card on the back of the machine
  (shorter, just the most common operations)
  
man -k "washing" = searching the appliance store's catalog
  by keyword to find which appliance does what you need
  
man section numbers = different books in the manual library:
  Book 1: how to operate (user commands)
  Book 2: how it works internally (system calls)
  Book 5: configuration file formats
```

---

### Gradual Depth - Five Levels

**Level 1:**
`man command` for full docs. `command --help` for quick summary.
`man -k keyword` to search. Navigate with /, n, q. That covers
90% of all documentation lookups.

**Level 2:**
Section numbers matter: `man 2 read` (system call) vs `man 1 read`
(bash read builtin). `whatis command` shows brief description and
which sections have a page. `apropos keyword` = `man -k keyword`.
man page formatting: SYNOPSIS `[option]` = optional; `<arg>` = required;
`...` = repeatable; `|` = OR.

**Level 3:**
`man -P less man` - man with a specific pager. `man -a command` -
show ALL sections with a page for command (one by one). `MANPATH`
environment variable: where man searches for pages. `manpath` command
shows current search path. `MANWIDTH=100 man command` - wider output
for wide terminals.

**Level 4:**
`info` pages (GNU info): more detailed than man, hyperlinked.
`info coreutils` = comprehensive GNU coreutils docs. Navigate:
`n` (next node), `p` (previous), `u` (up), `Enter` on link.
`pinfo` is a friendlier info browser. Man page sources: typically
`/usr/share/man/man1/` etc. Written in nroff/troff format (can
view with `cat /usr/share/man/man1/ls.1.gz | gunzip | man -l -`).

**Level 5:**
`tldr` (too long, didn't read): community-maintained simplified man
pages with practical examples. `apt install tldr && tldr tar`. Not
a replacement for man pages (less complete) but excellent for quick
"how do I...?" lookups. `cheat`: similar alternative. For kernel-level
documentation: `Documentation/` directory in kernel source. For
system calls: `man 2 syscall_name` and `/usr/share/doc/linux-doc/`.

---

### Code Example

**BAD - not using available help:**
```bash
# BAD 1: guessing flags
tar -czf archive.tgz ./dir -r  # -r is wrong! it's for appending to existing archives
# Causes: "tar: option requires an argument -- 'r'"

# BAD 2: searching internet for basic commands
# - finds outdated or OS-specific answers
# - may suggest deprecated flags
# - not specific to your installed version

# BAD 3: not reading SEE ALSO section
# Missing related commands that solve your actual problem better
```

**GOOD - using man pages and help effectively:**
```bash
# GOOD 1: quick help for flag lookup
find --help 2>&1 | grep "newer\|mtime"
# Quickly finds time-related flags without reading full manual

# GOOD 2: man page for complete understanding
man find
# Then inside man: /EXAMPLES for practical usage
# /mtime for time-based matching
# /exec for action flags

# GOOD 3: man -k when you don't know the command
man -k "compress"
# Shows: bzip2, gzip, lz4, zip, zstd - all compression commands
# Now you know ALL the options and can choose

# GOOD 4: reading SYNOPSIS section to understand all options
man grep
# SYNOPSIS shows: grep [OPTION]... PATTERN [FILE]...
# Sections: [OPTION] = optional, PATTERN = required, [FILE]...
# means zero or more files (reads stdin if no FILE)

# GOOD 5: section-specific lookup
man 5 passwd     # file format of /etc/passwd
man 5 crontab    # crontab file format (not the command)
man 2 fork       # fork() system call (C programmer reference)

# GOOD 6: find a command from its description
man -k "change directory"   # shows: cd - change the working directory
man -k "list directory"     # shows: ls, dir, vdir

# GOOD 7: tldr for practical examples
tldr tar          # shows: common tar operations with examples
tldr rsync        # quick rsync patterns
tldr curl         # common curl usage
```

---

### Man Page Anatomy

```
NAME
    ls - list directory contents        <- what it does (one line)

SYNOPSIS
    ls [OPTION]... [FILE]...            <- usage pattern
    ([] = optional, ... = repeatable)

DESCRIPTION
    Full explanation of the command...  <- detailed description

OPTIONS
    -a, --all
        list all files including hidden <- each flag documented

EXAMPLES                               <- practical usage examples
    ls -la /etc                        <- (not all man pages have this)

FILES                                  <- related files
    /etc/DIR_COLORS

SEE ALSO                               <- related commands
    dir(1), stat(1), ls(2)

BUGS                                   <- known issues
    ...

AUTHOR, COPYRIGHT, etc.
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Man pages are just for programmers" | Man pages document everything: user commands (section 1), configuration file formats (section 5), system admin commands (section 8). `man 5 passwd` explains /etc/passwd format. `man 8 useradd` explains the useradd command. Essential for all Linux users. |
| "--help gives the same info as man" | --help is a subset: short, fits on one screen, most common options. man is the complete reference: all options, explanations, examples, SEE ALSO. For a flag you know, --help is faster. For understanding, man is better. |
| "man pages are outdated" | Man pages are installed WITH the software package and match the installed version exactly. They're updated with each package release. They're more accurate than internet search results for your specific installed version. |
| "`man man` is circular/useless" | `man man` is genuinely useful. It explains man page sections, search syntax, MANPATH, formatting, and all man command options. Start there when learning man. |
| "You need internet to look things up" | Man pages, --help, and info are all offline. On an air-gapped production server, these are your only documentation resources. This is why mastering them is critical for production work. |

---

### Failure Modes & Diagnosis

**"No manual entry for X" (man page missing):**
```bash
# Error: No manual entry for docker-compose
# Cause 1: man page not installed
apt-get install docker-compose-doc   # some tools have separate doc packages
# Cause 2: tool doesn't have a man page (use --help)
docker-compose --help
# Cause 3: snap/flatpak installations don't always install man pages

# Install man pages for apt packages:
apt-get install manpages manpages-dev
# For POSIX/UNIX standard functions:
apt-get install manpages-posix
```

**Man page shows wrong version / missing flags:**
```bash
# Symptom: flag you know exists isn't in the man page
# Or: man page shows flags that don't work

# Cause: man page not updated / multiple versions installed

# Check which binary you're running:
which command
command --version

# Check if there's a newer man page:
man -a command   # shows ALL pages named "command" in order

# The authoritative source: --help flag (from the binary itself)
# is always current:
command --help 2>&1 | grep "the-flag-you-want"
```

---

### Related Keywords

**Foundational:**
LNX-006 (The Linux Terminal)

**Builds on this:**
LNX-024 (Shell Scripting), LNX-025 (find), LNX-026 (grep)

**Related:**
LNX-065 (POSIX Standards), LNX-044 (/etc Directory)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `man command` | Full manual page |
| `man -k keyword` | Search manual pages (= apropos) |
| `man N command` | Manual section N for command |
| `whatis command` | One-line description + section numbers |
| `command --help` | Brief usage summary |
| `command -h` | Shorter brief summary (some tools) |
| `info command` | GNU info documentation |
| `tldr command` | Practical examples (install separately) |
| `apropos keyword` | Search man pages (= man -k) |
| `man man` | Documentation about man itself |

**Man page section numbers:**
1 = User commands, 2 = System calls, 3 = Library functions,
4 = Device files, 5 = File formats, 6 = Games, 7 = Misc, 8 = Admin commands

**3 things to remember:**
1. `man command` for complete docs; `command --help` for quick flag lookup
2. `man -k keyword` to find commands when you don't know the command name
3. Section numbers matter: `man crontab` vs `man 5 crontab` (different pages!)

---

### Transferable Wisdom

The pattern of **built-in documentation** (man, --help, info) is the
model for all developer tooling: Python's `help()` built-in, Java's
javadoc (-help flags), Go's `go doc command`, kubectl's `--help` and
`kubectl explain`, Rust's `rustup doc`. Any mature system ships with
documentation. Mastering the documentation access pattern of any
ecosystem makes you self-sufficient.

The `man -k` keyword search pattern is the same as: `grep` through
documentation, IDE fuzzy search, Elasticsearch full-text search.
The skill: knowing what words to search for when you don't know the
exact answer - "man -k compress" finds gzip, bzip2, xz, zstd without
knowing their names.

---

### The Surprising Truth

The `man` command itself is documented in `man man`. But more
interesting: the original UNIX man pages were written in 1971 by
Dennis Ritchie and Ken Thompson. The FORMAT of man pages has been
essentially unchanged since then. The nroff/troff typesetting language
used to format them predates TeX (1978). When you read a man page today,
you're using a documentation system designed over 50 years ago, which
has survived the internet age, open source, the web, and AI assistance
largely unchanged - because it works. The same stability principle applies
to the commands themselves: `cat`, `grep`, `sed`, `awk` from the 1970s
still work identically today. This is Unix's most powerful feature:
backwards compatibility across decades.

---

### Mastery Checklist

- [ ] Can navigate a man page efficiently (search, jump to sections, quit)
- [ ] Can find a command's man page when you only know what it does (man -k)
- [ ] Can read SYNOPSIS notation ([option], <arg>, ...) correctly
- [ ] Can access section-specific man pages (man 5 crontab, man 2 fork)
- [ ] Can use --help effectively for quick flag lookups

---

### Think About This

1. You're on an air-gapped production server (no internet) and need to
   write a crontab entry, but you've forgotten the exact timing syntax.
   What command gives you the format reference? What about getting
   examples of common crontab patterns?

2. You're trying to understand what a specific /proc file contains
   (e.g., /proc/sys/net/core/somaxconn). Man pages don't seem to cover
   it. What documentation sources on the system might have this information?
   (Hint: there's a specific man section for configuration files and
   special files.)

3. `man -k "list"` returns hundreds of results. How would you refine
   the search to find only system administration commands that list things?
   What flag to man -k restricts results to a specific section?

**TYPE G:** A new engineer joins your team and will be working on a
Linux-based system without regular internet access. Design a 4-hour
documentation mastery curriculum that teaches them to be self-sufficient
using only built-in Linux documentation. What topics do you cover,
what practical exercises do you assign, and how do you test that they
can find any information they need without internet access?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you find help for a Linux command you've never used before?
A: Multiple approaches depending on what I need: (1) `command --help` for a quick overview of flags and usage - fast and always available. (2) `man command` for complete documentation including all options, examples, and related commands. I navigate with / to search and q to quit. (3) `man -k keyword` if I don't know the command name but know what I want to do (e.g., `man -k compress` shows all compression tools). (4) SEE ALSO section in man pages points to related commands. (5) `whatis command` for a one-line summary. (6) For file format references: `man 5 filename` (e.g., `man 5 crontab` for crontab syntax). On production servers without internet, man pages are often the only option, so mastering them is essential.

**Intermediate:**
Q: A man page entry says: `grep [OPTION]... PATTERN [FILE]...`. What does this SYNOPSIS syntax mean?
A: The SYNOPSIS uses standard notation: (1) `[OPTION]...` - square brackets = optional, `...` = can be repeated multiple times. So grep can take zero or more options. (2) `PATTERN` - no brackets = required. You must provide a search pattern. (3) `[FILE]...` - optional, repeatable. Zero or more files. If no files are given, grep reads from stdin. So you can run: `grep "error" file.log` (one file), `grep "error" *.log` (multiple files via glob expansion), or `cat file.log | grep "error"` (piped stdin with no FILE argument). This SYNOPSIS convention is standardized across POSIX man pages. Understanding it lets you read any man page and immediately know what's required vs optional.

**Expert:**
Q: How are man pages organized into sections, and why does the section distinction matter for developers?
A: Man pages are divided into numbered sections. For developers: (1) Section 1 - User commands: tools you run (`grep(1)`, `find(1)`, `tar(1)`). (2) Section 2 - System calls: kernel interface (`fork(2)`, `open(2)`, `read(2)`, `mmap(2)`). These are the C-level kernel interfaces your programs use. (3) Section 3 - Library functions: C standard library (`printf(3)`, `malloc(3)`, `pthread_create(3)`). (4) Section 5 - File formats: `/etc/passwd(5)`, `crontab(5)`, `resolv.conf(5)`. The distinction matters because the same name can exist in multiple sections: `open` is both a shell command (section 1) and a system call (section 2). `man open` gives section 1; `man 2 open` gives the system call documentation with the C function signature, error codes, and behavior. For Java developers: understanding `man 2 socket`, `man 2 connect`, `man 2 epoll_wait` explains what the JVM is actually doing when you open a ServerSocket or use NIO selectors - bridging the Java abstraction to the underlying Linux mechanism.
