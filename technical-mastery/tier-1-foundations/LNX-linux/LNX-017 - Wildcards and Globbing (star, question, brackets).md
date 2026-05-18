---
id: LNX-017
title: "Wildcards and Globbing (*, ?, [])"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-008
used_by: LNX-024, LNX-025
related: LNX-025, LNX-043, LNX-008
tags: [wildcards, globbing, shell-expansion, patterns, *, ?, [], brace-expansion]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/lnx/wildcards-and-globbing/
---

## TL;DR

Shell globbing expands wildcard patterns to matching filenames
BEFORE the command runs. `*` matches any characters, `?` matches
one character, `[abc]` matches one character from the set.
`rm *.log` deletes all .log files. The SHELL expands the glob;
the command sees the expanded list. Globbing and regular expressions
look similar but are NOT the same - globs are for filenames,
regex is for text content.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-017 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | wildcards, globbing, *, ?, [], brace expansion, shell patterns |
| **Prerequisites** | LNX-008 |

---

### The Problem This Solves

You have 1,000 log files named `app-2024-01-01.log` through
`app-2024-12-31.log`. You want to delete January's logs. Without
globbing: `rm app-2024-01-01.log app-2024-01-02.log ...` - list
each file individually. With globbing: `rm app-2024-01-*.log` -
the shell expands it to all matching files. This extends to
moving, copying, searching across any pattern of filenames.

---

### Textbook Definition

**Globbing** (filename expansion) is the shell's process of expanding
wildcard patterns to lists of matching files before passing them to
a command. The shell performs globbing; the command receives the
expanded list.

Glob patterns (NOT regular expressions):
- `*`: matches zero or more characters (but NOT `/`)
- `?`: matches exactly one character
- `[abc]`: matches one character from the set (a, b, or c)
- `[a-z]`: matches one character in the range a through z
- `[!abc]` or `[^abc]`: matches one character NOT in the set
- `**` (bash with globstar): matches across directories recursively

---

### Understand It in 30 Seconds

```bash
# * = any characters (zero or more)
ls *.log              # all files ending in .log
ls app*               # all files starting with "app"
ls app*.log           # files starting with "app" and ending with ".log"
rm /var/log/myapp/*.log.gz   # delete compressed logs

# ? = exactly one character
ls app-?.log          # app-1.log, app-a.log (not app-10.log)
ls file-??-2024.txt   # file-01-2024.txt, file-12-2024.txt

# [] = character class (one character from set)
ls app-[0-9].log      # app-0.log through app-9.log
ls [A-Z]*.md          # files starting with uppercase letter
ls app-[0-9][0-9].log # app-00.log through app-99.log
ls *.[ch]             # files ending in .c or .h

# Brace expansion (NOT globbing - generates text):
mkdir -p logs/{2023,2024}/{01,02,03}  # creates 6 directories
echo file{1..5}.txt   # file1.txt file2.txt file3.txt file4.txt file5.txt
cp file.txt{,.bak}    # copies file.txt to file.txt.bak

# Quoting prevents glob expansion:
grep "*.log" file.txt   # *.log stays as *.log (searching for literal)
echo '*.txt'            # prints: *.txt (not expanded)
```

---

### First Principles

**Who does the expansion:**
The critical insight: the SHELL expands globs, not the command.
`rm *.log` becomes `rm app.log nginx.log error.log` BEFORE rm runs.
rm never sees `*.log`. This means:
- If no files match: bash error "no match found" (or literal `*.log` passed)
- Remote commands can't use local globs: `ssh server "rm /logs/*.log"` works
  because the shell on the remote server expands the glob
- `ssh server rm /logs/*.log` fails - the LOCAL shell expands *.log
  to LOCAL files, not remote files

**Pattern character semantics:**
```
Glob: *.log      = any filename ending in .log
Regex: .*\.log   = any string ending in .log (very different!)

Glob *  = zero or more of any character
Regex * = zero or more of the PREVIOUS character

Glob ?  = any SINGLE character
Regex ? = zero or one of the PREVIOUS character

They look similar but are completely different systems.
Globs: filename matching in shell
Regex: pattern matching in text (grep, sed, awk, Java, Python)
```

---

### Thought Experiment

Imagine you need to process all JSON files from December 2024 in a
logs directory. The files are named: `service-2024-12-01.json` through
`service-2024-12-31.json`.

Without globbing:
```bash
for d in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31; do
    cat service-2024-12-$d.json >> december.json
done
```

With globbing:
```bash
cat service-2024-12-*.json >> december.json
```

The glob `service-2024-12-*.json` expands to all 31 files in
alphabetical order (which happens to be chronological for this naming
scheme). One command, no loop needed.

---

### Mental Model / Analogy

Globs are like **search queries for filenames** in a file cabinet:

```
File cabinet = directory
File folders = files with names

"Give me all folders named *.report"
  = all folders whose name ENDS WITH ".report"
  The clerk looks through the cabinet and hands you matching folders
  
"Give me folder report-?.txt"
  = folder named "report-" then ONE more character, then ".txt"
  = matches: report-1.txt, report-a.txt
  = does NOT match: report-10.txt (two chars after -)
  
"Give me all folders starting with [A-M]"
  = folders whose first letter is A through M
  
Brace expansion = "make me these specific things":
  mkdir {January,February,March}
  = make three folders named exactly those three names
```

---

### Gradual Depth - Five Levels

**Level 1:**
`*` = any characters. `?` = one character. `[abc]` = one of a, b, c.
Quote globs when you want literal * (e.g., in grep patterns).
Brace expansion `{a,b,c}` generates text, not filename matches.

**Level 2:**
`shopt -s globstar` enables `**` for recursive matching:
`ls **/*.log` = all .log files in any subdirectory.
`shopt -s dotglob` makes `*` include dotfiles (hidden files
starting with `.`). `shopt -s nullglob` returns empty string instead
of error when no files match.

**Level 3:**
Extended globbing (shopt -s extglob):
- `?(pattern)`: zero or one match
- `*(pattern)`: zero or more matches
- `+(pattern)`: one or more matches
- `@(pattern)`: exactly one match
- `!(pattern)`: anything NOT matching pattern
Example: `ls !(*.log)` = all files except .log files.

**Level 4:**
Glob vs regex in scripts: `[[ "$filename" == *.log ]]` uses glob
matching (== with double brackets). `[[ "$filename" =~ \.log$ ]]`
uses regex matching (=~). In find: `-name "*.log"` uses glob.
`-regex ".*\.log"` uses regex. These are different systems and
mixing them up causes subtle bugs.

**Level 5:**
In production scripting: never rely on alphabetical glob expansion
for order (locale-dependent). Prefer explicit loops with sort when
order matters. For large directories (100K+ files), glob expansion
can cause "Argument list too long" (ARG_MAX limit). Fix: use
find + xargs instead of glob: `find /logs -name "*.log" | xargs rm`.

---

### Code Example

**BAD - glob anti-patterns:**
```bash
# BAD 1: glob passed to remote command without quoting
ssh server rm /logs/*.log
# Shell expands *.log on LOCAL machine first!
# Sends: rm /logs/localfile1.log /logs/localfile2.log (wrong files!)

# Fix: quote to prevent local expansion:
ssh server 'rm /logs/*.log'   # remote shell expands it

# BAD 2: unquoted glob in grep (tries to glob-expand the pattern)
grep *.txt /var/log/syslog    # *.txt expands to LOCAL txt files!
# grep then searches those files for /var/log/syslog (wrong!)

# Fix: always quote regex patterns:
grep ".*\.txt" /var/log/syslog  # or single quotes

# BAD 3: rm with unintended glob match
rm * .log    # WRONG! removes ALL files + a file named ".log"
rm *.log     # CORRECT: removes only .log files

# BAD 4: ARG_MAX overflow for very large directories
rm /logs/*.log  # fails if too many files: "Argument list too long"
# Fix: use find + xargs
find /logs -maxdepth 1 -name "*.log" -delete
```

**GOOD - correct glob usage:**
```bash
# GOOD 1: backup before rm with glob
ls *.log            # verify what would be deleted first
rm *.log            # then delete

# GOOD 2: process multiple file types
for file in *.{log,txt,csv}; do
    echo "Processing: $file"
    process "$file"
done

# GOOD 3: check if any files match before processing
shopt -s nullglob   # glob returns empty string if no match
files=(*.log)
if [ ${#files[@]} -eq 0 ]; then
    echo "No log files found"
    exit 0
fi
# process ${files[@]}

# GOOD 4: recursive search with globstar
shopt -s globstar
for log in /var/log/**/*.log; do
    tail -1 "$log"   # last line of each log file
done

# GOOD 5: safe temp file cleanup
# Instead of:
rm /tmp/*.tmp
# Use (safer - only removes YOUR temp files):
rm /tmp/myapp_*.tmp

# GOOD 6: brace expansion for creating directory structures
mkdir -p /var/data/{raw,processed,archive}/{2023,2024}
# Creates: /var/data/raw/2023, /var/data/raw/2024,
#          /var/data/processed/2023, etc. (6 directories)
```

---

### Comparison Table

| Feature | Glob | Regex |
|---------|------|-------|
| Used for | Filename matching | Text content matching |
| `*` means | Any chars (zero+) | Zero or more of PREVIOUS char |
| `?` means | Any one char | Zero or one of PREVIOUS char |
| `.` means | Literal dot | Any single character |
| Used by | Shell, find -name | grep, sed, awk, Java, Python |
| In bash `[[` | `== pattern` (glob) | `=~ pattern` (regex) |
| Example | `*.log` | `.*\.log$` |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`*` in glob = `.*` in regex" | `*` in glob = zero or more of ANY character. In regex, `*` = zero or more of the PREVIOUS character; `.*` = any characters. They accidentally produce similar results in simple cases but are completely different syntaxes. |
| "Globs work in grep patterns" | `grep *.log file` - the shell expands `*.log` to local filenames BEFORE grep runs. grep never sees the pattern. Always quote grep patterns: `grep "\.log$" file` or `grep '\.log$' file`. |
| "`?` matches zero or one character" | In globbing, `?` matches EXACTLY one character. Zero characters: no match. In regex, `?` means zero or one of the previous character. |
| "Globs can cross directory boundaries" | `*` does NOT match `/`. `*.log` matches `app.log` but not `logs/app.log`. Use `**` with globstar enabled, or `find`, for recursive matching. |
| "Brace expansion is globbing" | Brace expansion `{a,b,c}` is different: it generates text combinations regardless of whether files exist. `file{1,2,3}.txt` → `file1.txt file2.txt file3.txt` even if those files don't exist. Globbing only returns files that exist. |

---

### Failure Modes & Diagnosis

**No files match, command gets literal glob:**
```bash
# Behavior varies by shell setting:
# Default bash: passes literal *.log to command if no files match
rm *.log   # if no .log files: "rm: cannot remove '*.log': No such file"
           # (passes the literal string "*.log" to rm)

# Fix: check before operating, or use nullglob:
shopt -s nullglob   # glob expands to nothing if no match
files=(*.log)
if [ ${#files[@]} -gt 0 ]; then
    rm "${files[@]}"
fi
```

**ARG_MAX exceeded (too many files):**
```bash
# Error: bash: /bin/rm: Argument list too long
# Cause: glob expands to 100,000 filenames, exceeding ARG_MAX (~2MB)
rm /var/log/old/*.log

# Fix: use find with -delete (no argument list limit):
find /var/log/old -maxdepth 1 -name "*.log" -delete

# Or: xargs with a reasonable chunk size:
find /var/log/old -maxdepth 1 -name "*.log" | xargs -r rm
```

**Security: glob injection in scripts:**
```bash
# Risk: user-controlled input used in glob context
# BAD: user provides filename with glob characters
user_input="*.conf"    # could be * (matches everything!)
ls $user_input         # lists ALL files!

# GOOD: quote the variable to prevent glob expansion
ls "$user_input"       # looks for a file literally named "*.conf"

# GOOD: validate input before using:
if [[ "$user_input" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    ls "$user_input"
else
    echo "Invalid filename"
fi
```

---

### Related Keywords

**Foundational:**
LNX-008 (Files and Directories)

**Builds on this:**
LNX-025 (find), LNX-024 (Shell Scripting),
LNX-043 (Regular Expressions)

**Related:**
LNX-026 (grep), LNX-042 (Bash Scripting)

---

### Quick Reference Card

| Pattern | Matches |
|---------|---------|
| `*.log` | Any filename ending in .log |
| `app*` | Any filename starting with app |
| `app-?.txt` | app-1.txt, app-a.txt (one char) |
| `[0-9]*` | Files starting with a digit |
| `[!.]*` | Files NOT starting with dot |
| `*.{log,txt}` | Files ending in .log or .txt |
| `file{1..5}.txt` | file1.txt through file5.txt |
| `**/*.log` | All .log files recursively (need globstar) |

**3 things to remember:**
1. SHELL expands globs before the command runs - always quote when you want literal `*` (in grep, ssh, etc.)
2. Globs and regex are different: glob `*` = any chars; regex `*` = zero or more of previous char
3. For huge directories: use `find -delete` or `xargs` instead of glob (avoids ARG_MAX limit)

---

### Transferable Wisdom

Glob patterns appear far beyond the shell. Many systems use
glob-like syntax: `.gitignore` files use globs to specify ignored
paths; `docker .dockerignore` uses the same pattern; `find -name`
uses globs; Maven `<include>**/*.java</include>` uses ant-style
globs; Spring's `@PathVariable("/api/{id}")` URL patterns. The
`*` = any characters in filename context is a universal convention.

The distinction between **pattern matching on filenames** (globbing)
and **pattern matching on text content** (regex) is a fundamental
Unix concept. Getting this wrong causes cryptic bugs - especially when
passing unquoted patterns to commands via scripts.

---

### The Surprising Truth

When you run `echo *` in bash, the shell performs glob expansion and
passes the expanded list to echo. So `echo *` prints all filenames
in the current directory - essentially a simple version of `ls`. If
you're in a directory with no files, bash passes the literal `*` to
echo, which prints a star. But `ls *` without globstar cannot list
the contents of subdirectories recursively... until you realize that
`*` expands to include directory names, and ls lists the contents of
any directory names it receives. So `ls *` actually lists both files
AND the contents of immediate subdirectories - one level deep only,
without recursion. This surprises developers used to `ls *` in other
contexts like Windows where `dir *` doesn't expand this way.

---

### Mastery Checklist

- [ ] Can use *, ?, and [] to match filename patterns
- [ ] Can explain that the shell expands globs before the command runs
- [ ] Can correctly quote globs when passing to remote commands (ssh) or grep
- [ ] Can use brace expansion to create multiple paths/files at once
- [ ] Can explain when to use find instead of globs (recursive, large directories)

---

### Think About This

1. You run `ssh server rm /logs/*.log` and it deletes files on your
   local machine instead of on the server. What happened? How do you
   fix the command?

2. Your shell script has `for file in *.log; do process "$file"; done`.
   What happens if there are no .log files in the current directory?
   How does the behavior differ between bash (default) and bash with
   `shopt -s nullglob`? Which is safer for production scripts?

3. `ls **/*.log` doesn't work as expected (only shows files one level
   down, not recursively). What shell option do you need to enable,
   and what is a reliable alternative that works without any shell
   options and across all POSIX shells?

**TYPE G:** You're writing a deployment script that needs to process
all configuration files matching `*.conf` across a complex directory
tree with 50,000+ files, some directories require sudo access, and
the script must handle file names with spaces and special characters.
The script must be both safe (no glob injection, no argument list
overflow) and efficient (no unnecessary file reads). What implementation
approach would you use?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between globbing and regular expressions?
A: Both use pattern matching, but for completely different purposes. Globbing (shell filename expansion) matches filenames: `*` = any sequence of characters, `?` = exactly one character, `[abc]` = one character from set. Regular expressions match text content: `*` = zero or more of the PREVIOUS character, `?` = zero or one of previous character, `.` = any one character. They look similar but are fundamentally different: `*.log` in a glob means files ending in .log; the equivalent regex is `.*\.log$`. Globbing is done by the SHELL before the command runs; the command receives the expanded list of filenames. Regular expressions are processed by the command (grep, sed, awk, Java Pattern) on the text content of files. Common mistake: passing an unquoted glob to grep (`grep *.log file`) - the shell expands `*.log` to local filenames before grep runs.

**Intermediate:**
Q: Explain what happens when you run `ssh remotehost rm /tmp/*.log`.
A: The local shell expands the glob `*.log` first - it looks for files matching `*.log` in the local machine's /tmp directory. If matches are found, the command becomes something like `ssh remotehost rm /tmp/local1.log /tmp/local2.log` - which tries to remove local filenames from the remote server's /tmp directory (almost certainly wrong). If no matches are found locally, bash passes the literal `*.log` to ssh (as a shell argument), and the remote shell would try to expand it. The fix: quote the glob so the local shell doesn't expand it: `ssh remotehost 'rm /tmp/*.log'`. With single quotes, the literal string `rm /tmp/*.log` is sent to the remote shell, which expands the glob on the remote host's /tmp directory.

**Expert:**
Q: A shell script runs `rm $user_provided_dir/*.log`. What are the security implications, and how do you make this safe?
A: Multiple risks: (1) Path traversal: user provides `../../etc/` - deletes system config files. (2) Glob injection: user provides a path containing glob chars `[ab]` - matches unexpected files. (3) Argument injection: user provides a path with spaces or special characters. (4) If `$user_provided_dir` is empty: `rm /*.log` - attempts to delete root filesystem log files! Safe implementation: (1) validate the input: `if [[ "$user_provided_dir" =~ ^[a-zA-Z0-9/_.-]+$ ]]; then echo "Invalid"; exit 1; fi`; (2) resolve the canonical path and verify it's within the expected base: `real_dir=$(realpath "$user_provided_dir")` then `[[ "$real_dir" == /allowed/base/* ]]`; (3) quote the variable: `"$user_provided_dir"/*.log`; (4) check if variable is non-empty: `${user_provided_dir:?must not be empty}`; (5) use find for large directories instead of glob to avoid ARG_MAX; (6) test with `ls` before `rm` during development; (7) consider using `--` to end option parsing: `rm -- "$user_provided_dir"/*.log`.
