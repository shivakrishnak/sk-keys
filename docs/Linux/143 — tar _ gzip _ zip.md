---
layout: default
title: "tar / gzip / zip"
parent: "Linux"
nav_order: 143
permalink: /linux/tar-gzip-zip/
number: "0143"
category: Linux
difficulty: ★☆☆
depends_on: Linux File System Hierarchy, Shell (bash, zsh), File Permissions (chmod, chown)
used_by: CI/CD, SCP / rsync, Shell Scripting, Package Managers (apt, yum, dnf)
related: SCP / rsync, find / xargs, curl / wget
tags:
  - linux
  - os
  - devops
  - foundational
---

# 143 — tar / gzip / zip

⚡ TL;DR — `tar` bundles files and directories into a single archive preserving metadata; `gzip`/`bzip2`/`xz` compress it; `zip` bundles and compresses in one step for cross-platform use.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to send a project directory (3,000 files) to a colleague. You can copy them one-by-one over the network — 3,000 separate transfers, each with TCP handshake overhead, losing file permissions and symlinks. Alternatively you can compress individual files but then you have 3,000 compressed files, still no way to transfer directory structure or metadata.

**THE BREAKING POINT:**
A backup script copies a 5 GB directory over the network nightly. The transfer takes 45 minutes because thousands of small files each incur connection overhead. File permissions are not preserved, so the restored backup requires manual `chmod` to work again.

**THE INVENTION MOMENT:**
This is exactly why `tar` (Tape ARchive) was created. It serialises an entire directory tree — files, directories, permissions, ownership, symlinks, timestamps — into a single byte stream that can be compressed as a unit and transferred with a single connection.

---

### 📘 Textbook Definition

`tar` is an archiving utility that combines multiple files and directories into a single archive file (`.tar`), preserving filesystem metadata (permissions, ownership, timestamps, symlinks, hard links). It does not compress by default; compression is provided by separate filters: `gzip` (`.gz`, fast), `bzip2` (`.bz2`, better compression), `xz` (`.xz`, best compression, slowest). `zip` is a self-contained format that bundles and compresses in one step using DEFLATE, with native support on Windows and macOS.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
tar packs a directory into one file; gzip shrinks it; together they create portable, compressed archives.

**One analogy:**
> `tar` is like a moving company that packs every item from a house into labelled boxes, records the room each box came from and who owns it. `gzip` is the vacuum packer that shrinks each box. Together, you ship one compressed, labelled container instead of hundreds of loose items.

**One insight:**
`tar` and compression are deliberately separate tools. This means you can stream `tar` output directly to `gzip` without creating an intermediate file, and `tar` can pipe output to `ssh` to transfer archives across the network with no temporary file on disk.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An archive must preserve all filesystem metadata, not just file contents.
2. Compression works best on a single stream (compressing many small files individually misses cross-file redundancy).
3. Cross-platform compatibility requires a standard format with broad tool support.

**DERIVED DESIGN:**
`tar` serialises the directory tree as a sequential stream of 512-byte header blocks (containing filename, permissions, ownership, timestamps) followed by file content blocks. This design dates from magnetic tape storage (sequential access only) — the sequential format is still optimal for streaming over networks and through compressors.

`gzip` uses LZ77 + Huffman coding on the byte stream. Because it compresses the entire archive as one stream, it exploits cross-file redundancy that per-file compression misses — critical for directories of similar source files (e.g., Java class files or HTML templates).

**THE TRADE-OFFS:**
**tar.gz gain:** Preserves all metadata, efficient compression on similar files, streamable.
**tar.gz cost:** Cannot random-access individual files without decompressing the entire archive; not natively readable on Windows without third-party tools.
**zip gain:** Random-access to individual files (each file compressed independently), native Windows/macOS support.
**zip cost:** Slightly worse compression (no cross-file redundancy), less metadata preservation.

---

### 🧪 Thought Experiment

**SETUP:**
You have 10,000 Java `.class` files totalling 200 MB that need to be transferred to a remote server and extracted there.

**WHAT HAPPENS with individual gzip:**
Each `.class` file is compressed individually: `gzip *.class`. Each 20 KB file compresses to maybe 18 KB (little benefit — small files). The cross-file redundancy (all class files share JVM bytecode patterns) is lost. You still have 10,000 files to transfer. No metadata preserved.

**WHAT HAPPENS with tar.gz:**
`tar czf classes.tar.gz *.class` — tar serialises all 10,000 files into one stream; gzip compresses the whole stream, exploiting the shared patterns across all class files. Compression ratio: 200 MB → 45 MB. One file to transfer. Permissions, timestamps preserved. Remote extraction: `tar xzf classes.tar.gz`.

**THE INSIGHT:**
Compressing a tar archive (the whole stream at once) is fundamentally different from compressing individual files — it exploits redundancy across file boundaries that per-file compression cannot see.

---

### 🧠 Mental Model / Analogy

> Imagine shipping books overseas. `tar` is the box — it holds all books, with a catalogue showing which shelf each came from and who owns it. `gzip` is the vacuum seal on the box — it squeezes all air out of the contents as a whole (exploiting that most books share common words). `zip` is a FedEx prepacked envelope with built-in compression — each book vacuum-sealed individually, then all put in one envelope.

- "Box with catalogue" → tar archive with metadata headers
- "Vacuum seal on whole box" → gzip compressing the whole stream
- "Shared common words across books" → cross-file redundancy gzip exploits
- "Each book vacuum-sealed individually" → zip compresses each file independently

Where this analogy breaks down: with tar streaming, the "box" never needs to exist on disk — the entire create-compress-transfer pipeline can be streamed without any intermediate file.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`tar` packs a whole folder into one file, preserving everything (permissions, dates, structure). `gzip` squishes that file to save space. Together they're the standard way to bundle and compress files on Linux. `zip` does the same but in a format that Windows and Mac understand natively.

**Level 2 — How to use it (junior developer):**
Create: `tar czf archive.tar.gz dirname/` — creates a compressed archive. Extract: `tar xzf archive.tar.gz` — extracts in the current directory. List contents without extracting: `tar tzf archive.tar.gz`. For zip: `zip -r archive.zip dirname/` and `unzip archive.zip`. The flags for tar: `c`=create, `x`=extract, `z`=gzip, `j`=bzip2, `J`=xz, `f`=filename, `v`=verbose.

**Level 3 — How it works (mid-level engineer):**
tar reads the directory tree via readdir/stat system calls and writes 512-byte POSIX header blocks followed by file data blocks. The archive is a byte stream — no index, no random access. gzip wraps this stream in LZ77+Huffman. The key insight is that `tar c dirname | gzip | ssh server "tar x -C /dest"` streams the entire operation: no temp file created locally or remotely, data decompresses in-flight on the destination. This is useful for large directory migrations with limited disk space.

**Level 4 — Why it was designed this way (senior/staff):**
tar's 512-byte block format was chosen for compatibility with tape drives (blocking factor). The format has evolved through POSIX.1-1988, GNU tar extensions, and pax (POSIX.1-2001 extended headers for long filenames and large files). The separation of archiving (tar) from compression (gzip/bzip2/xz) is the Unix philosophy at work — each tool does one thing and they compose. Modern archives like `.tar.zst` (zstd compression) achieve better ratios than gzip at faster speeds, increasingly used in package managers.

---

### ⚙️ How It Works (Mechanism)

**tar archive structure:**
```
┌─────────────────────────────────────────────┐
│  TAR ARCHIVE FORMAT (simplified)           │
└─────────────────────────────────────────────┘

  [512-byte header: filename, permissions,
   owner, size, mtime, type, link target]
  [File data (padded to 512-byte boundary)]
  [512-byte header: next file...]
  [File data...]
  ...
  [Two 512-byte zero blocks: end of archive]
```

**Common tar commands:**
```bash
# Create compressed archive (gzip)
tar czf archive.tar.gz dirname/

# Create with bzip2 (better compression, slower)
tar cjf archive.tar.bz2 dirname/

# Create with xz (best compression, slowest)
tar cJf archive.tar.xz dirname/

# Create with zstd (fast + good compression)
tar --zstd -cf archive.tar.zst dirname/

# Verbose output during create
tar czvf archive.tar.gz dirname/

# Extract in current directory
tar xzf archive.tar.gz

# Extract to specific directory
tar xzf archive.tar.gz -C /target/dir/

# List contents without extracting
tar tzf archive.tar.gz

# Extract single file from archive
tar xzf archive.tar.gz path/to/specific/file.txt

# Create archive from find output (exclude .git)
find src/ -not -path '*/.git/*' -print0 | \
  tar czf archive.tar.gz --null -T -

# Streaming: create on server1, extract on server2
tar czf - /data | ssh server2 "tar xzf - -C /data"
```

**gzip commands:**
```bash
gzip file.txt         # compress: file.txt → file.txt.gz
gzip -d file.txt.gz   # decompress
gunzip file.txt.gz    # same as gzip -d
gzip -k file.txt      # keep original file too
gzip -l file.txt.gz   # show compression info
gzip -9 file.txt      # best compression (slowest)
gzip -1 file.txt      # fastest compression
zcat file.txt.gz      # view compressed file without extract
```

**zip commands:**
```bash
# Create zip archive
zip -r archive.zip dirname/

# Create with max compression
zip -9 -r archive.zip dirname/

# Exclude patterns
zip -r archive.zip dirname/ -x "*.log" -x ".git/*"

# List contents
unzip -l archive.zip

# Extract
unzip archive.zip

# Extract to specific directory
unzip archive.zip -d /target/dir/

# Extract specific file
unzip archive.zip path/to/file.txt
```

**Compression comparison:**
```
File: Linux kernel source (800 MB of C code)

gzip  (-6 default): 270 MB  | compress: 5s  | decompress: 2s
bzip2 (-9):         220 MB  | compress: 35s | decompress: 12s
xz    (-6 default): 185 MB  | compress: 90s | decompress: 8s
zstd  (default):    240 MB  | compress: 3s  | decompress: 1s
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  BUILD ARTIFACT PACKAGING PIPELINE         │
└─────────────────────────────────────────────┘

 CI build completes → /build/ directory ready
       │
       ▼
tar czf app-v2.0.tar.gz build/  ← YOU ARE HERE
       │  metadata preserved, compressed
       ▼
sha256sum app-v2.0.tar.gz > app-v2.0.sha256
       │  integrity fingerprint
       ▼
Artifact uploaded to S3 / release server
       │
       ▼
Deploy: wget/curl downloads .tar.gz
       │
       ▼
sha256sum --check app-v2.0.sha256  (verify)
       │
       ▼
tar xzf app-v2.0.tar.gz -C /opt/app/
       │
       ▼
Service restarted with new binary
```

**FAILURE PATH:**
Corrupted archive (truncated download) → `tar xzf` fails with "gzip: stdin: unexpected end of file" → extraction aborts partially → target directory may be inconsistent. Always verify checksum before extracting.

**WHAT CHANGES AT SCALE:**
At scale (multi-GB ML model archives, container layer tarballs) parallel compression tools are used: `pigz` (parallel gzip), `pbzip2` (parallel bzip2), `zstd --threads=N`. Docker image layers are individually compressed tar archives (`.tar.gz`) — Docker's union filesystem layers each as a separate archive and caches them by content hash.

---

### 💻 Code Example

**Example 1 — BAD: missing compression, wrong extract:**
```bash
# BAD — no compression (big archive)
tar cf archive.tar dirname/

# BAD — extracts to current dir, may overwrite files
tar xzf archive.tar.gz
```

**Example 1 — GOOD: compressed, extract to known location:**
```bash
# GOOD — compressed, verbose, known target
tar czf app-$(date +%Y%m%d).tar.gz src/

# GOOD — extract to explicit directory
mkdir -p /opt/app
tar xzf app-20240115.tar.gz --strip-components=1 \
  -C /opt/app/
# --strip-components=1 removes the top-level dirname
```

**Example 2 — Streaming backup without temp file:**
```bash
# Stream tar directly to remote server
# No temporary file created on either side
tar czf - /important/data | \
  ssh backup-server "cat > /backups/data-$(date +%Y%m%d).tar.gz"

# Even better: stream and encrypt
tar czf - /secrets | \
  gpg --symmetric --cipher-algo AES256 | \
  ssh backup-server "cat > /backups/secrets-$(date +%Y%m%d).tar.gz.gpg"
```

**Example 3 — Exclude patterns and verify:**
```bash
# Create archive excluding development artifacts
tar czf release.tar.gz src/ \
  --exclude='**/node_modules' \
  --exclude='**/.git' \
  --exclude='**/*.test.js' \
  --exclude='**/.DS_Store'

# Verify archive integrity and list contents
tar tzf release.tar.gz | wc -l   # count files
tar tzf release.tar.gz | head -20  # spot check

# Generate checksum for distribution
sha256sum release.tar.gz > release.tar.gz.sha256
cat release.tar.gz.sha256
```

---

### ⚖️ Comparison Table

| Format | Compression | Cross-platform | Random Access | Best For |
|---|---|---|---|---|
| **.tar.gz** | Good, fast | Linux/Mac native | No | Linux deployment, backups |
| .tar.bz2 | Better | Linux/Mac native | No | Space-constrained archives |
| .tar.xz | Best | Linux/Mac native | No | Distribution packages |
| **.zip** | Good | Universal | Yes (per-file) | Windows sharing, web downloads |
| .tar.zst | Good+fast | Requires zstd | No | Modern CI/CD, Docker layers |
| .7z | Excellent | Requires 7zip | Yes | Maximum compression |

How to choose: use `.tar.gz` for Linux server deployments and scripts; use `.zip` when the recipient may use Windows or macOS without terminal tools; use `.tar.zst` in modern CI pipelines where speed matters.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| tar compresses files | tar only archives; compression is done by a separate filter (-z for gzip, -j for bzip2, -J for xz) |
| `tar xzf archive.tar.gz` always extracts safely | Without `-C target/`, files extract relative to the current directory; a maliciously crafted archive can include `../` path traversal paths |
| zip and tar.gz are equivalent | zip compresses each file independently (no cross-file compression); tar.gz compresses the entire stream (better ratio for similar files) |
| gzip and gunzip are different programs | They are the same binary; gunzip is a symlink to gzip |
| Extracting a tar archive is always safe | Archive files can contain absolute paths or `../` traversal — always inspect with `tar tz` before extracting untrusted archives |

---

### 🚨 Failure Modes & Diagnosis

**Zip Slip (Path Traversal in Archive)**

**Symptom:**
Extracting an archive overwrites unexpected files outside the target directory.

**Root Cause:**
A maliciously crafted archive contains entries with paths like `../../etc/cron.d/evil`. Tools like `unzip` and some versions of tar follow these paths during extraction.

**Diagnostic Command:**
```bash
# ALWAYS inspect archive contents before extracting
tar tzf untrusted.tar.gz | grep '\.\.'
unzip -l untrusted.zip | grep '\.\.'
```

**Fix:**
```bash
# Extract to an isolated directory and inspect
mkdir /tmp/safe-extract
tar xzf archive.tar.gz -C /tmp/safe-extract
# Review before moving to production path
```

**Prevention:**
Never extract untrusted archives with root privileges; always inspect contents first; use `--strip-components` to normalise paths.

---

**Corrupted Archive (Truncated Download)**

**Symptom:**
`tar xzf archive.tar.gz` fails mid-extraction with "gzip: stdin: unexpected end of file" or "tar: Unexpected EOF in archive".

**Root Cause:**
The download was interrupted or the file was partially written, resulting in a truncated gzip stream.

**Diagnostic Command:**
```bash
# Test archive integrity without extracting
gzip -t archive.tar.gz && echo "OK" || echo "CORRUPTED"
tar tzf archive.tar.gz > /dev/null && echo "OK"
```

**Fix:**
Re-download the archive; verify against a published SHA256 checksum.

**Prevention:**
Always verify checksum after download: `sha256sum --check archive.sha256`.

---

**Archive Consumes All Disk Space**

**Symptom:**
`tar xzf archive.tar.gz` fills the disk completely and fails.

**Root Cause:**
The compressed archive is small but expands to a very large uncompressed size (compression ratio of 50:1 is common for text).

**Diagnostic Command:**
```bash
# Check uncompressed size before extracting
gzip -l archive.tar.gz   # shows uncompressed size
# Or with tar
tar tzf archive.tar.gz | \
  awk 'NR>1{sum+=$3} END{printf "%.1f MB\n", sum/1048576}'
```

**Fix:**
Ensure sufficient disk space before extraction; extract to a volume with adequate capacity.

**Prevention:**
Always check uncompressed size before extracting archives from unknown sources; monitor disk space in extraction scripts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Linux File System Hierarchy` — tar preserves directory structure; knowing the FHS helps with extraction paths
- `Shell (bash, zsh)` — tar/gzip/zip are shell commands; understanding shell pipelines is needed for streaming usage
- `File Permissions (chmod, chown)` — tar preserves permissions; understanding them is needed to know what gets preserved

**Builds On This (learn these next):**
- `CI/CD` — build artifacts are typically packaged as tar.gz archives for deployment
- `SCP / rsync` — archives are often transferred using scp or rsync after creation
- `Docker` — Docker image layers are tar archives stored in a registry as compressed blobs

**Alternatives / Comparisons:**
- `zip` — cross-platform alternative with per-file compression and random access
- `zstd` — modern compression algorithm (used in `.tar.zst`) faster and better than gzip
- `rsync` — for synchronising live directories without creating an archive first

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ tar: archive tool preserving metadata;    │
│              │ gzip/zip: compression algorithms          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Thousands of files are slow to transfer   │
│ SOLVES       │ individually and lose metadata            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ tar czf streams to gzip — no temp file    │
│              │ needed; compresses cross-file redundancy  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Packaging build artifacts, creating       │
│              │ backups, distributing software            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need random file access (use zip);        │
│              │ Windows recipients without tools (zip)    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ tar.gz: better compression ratio vs       │
│              │ zip: random access + native Windows       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "tar packs the box; gzip shrinks it;      │
│              │  one command, one file, all metadata"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ zstd → Docker layers → OCI Image spec    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Dockerfile runs `COPY app.tar.gz /tmp/ && RUN tar xzf /tmp/app.tar.gz -C /opt/app && RUN rm /tmp/app.tar.gz`. A security review flags this as creating unnecessary image layers and keeping secrets in intermediate layers. Redesign the Dockerfile commands to minimise layer count, reduce image size, and ensure the tar file doesn't persist in any image layer.

**Q2.** You receive a tar archive from a vendor that is 50 MB compressed. Extracting it fills your disk and fails at 80% completion. `gzip -l` shows the uncompressed size as 42 GB. Trace the sequence of kernel and filesystem operations that occur during extraction, explain why the disk fills gradually rather than immediately, and design a safer extraction workflow that verifies available disk space before committing to extraction.
