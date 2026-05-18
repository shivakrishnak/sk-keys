---
id: LNX-029
title: "Archives and Compression (tar, gzip, zip, bzip2)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-007, LNX-008
used_by: LNX-024, LNX-068
related: LNX-025, LNX-008, LNX-068
tags: [tar, gzip, zip, bzip2, xz, compression, archive, backup, deployment]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/lnx/archives-compression/
---

## TL;DR

Two operations: **archiving** (bundling files into one) and
**compression** (reducing size). `tar` archives (and can compress).
`gzip`/`bzip2`/`xz` compress. The universal workflow: `tar czf archive.tar.gz directory/`
to create, `tar xzf archive.tar.gz` to extract. Flags mnemonic:
`czf` = **c**reate, **z** (gzip), **f** (file). `xzf` = e**x**tract,
**z** (gzip), **f** (file). `tar tvf archive.tar.gz` to list contents.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-029 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | tar, gzip, bzip2, xz, zip, compress, archive, backup |
| **Prerequisites** | LNX-007, LNX-008 |

---

### The Problem This Solves

Transfer 10,000 Java source files to another server. Without archiving:
transfer 10,000 individual HTTP/SCP requests (slow, overhead per file).
With tar: one request, one file. With compression: that one file is 5-10x
smaller. Log rotation: roll daily logs into a compressed archive (200MB
raw -> 10MB gzipped). Application packaging: ship the JAR + config + scripts
as one bundle. Backup: snapshot a directory to a single file for storage.

---

### Textbook Definition

**tar** (tape archive): Combines multiple files into a single archive
file (.tar), preserving directory structure, permissions, ownership,
and timestamps. tar itself does not compress. Named for tape archive
(magnetic tape era).

**gzip**: Compression algorithm (DEFLATE). Compresses a single file.
Extension: `.gz`. Typically 60-80% size reduction on text.

**bzip2**: Higher compression ratio than gzip, slower. Extension: `.bz2`.

**xz**: Highest compression ratio, slowest. Extension: `.xz`.
Often used for Linux distribution packages.

**zip**: Cross-platform archive + compression combined (unlike tar+gzip).
Native to Windows. Supported on Linux. Extension: `.zip`.

**Combined formats:**
- `.tar.gz` or `.tgz`: tar + gzip (most common)
- `.tar.bz2`: tar + bzip2
- `.tar.xz`: tar + xz (best compression, used for distro packages)

---

### Understand It in 30 Seconds

```bash
# CREATE archives:
tar czf archive.tar.gz directory/        # create gzipped tar
tar czf logs.tar.gz /var/log/myapp/      # archive logs directory
tar cjf archive.tar.bz2 directory/       # bzip2 compression
tar cJf archive.tar.xz directory/        # xz compression (best ratio)

# EXTRACT archives:
tar xzf archive.tar.gz                   # extract here
tar xzf archive.tar.gz -C /target/dir/  # extract to specific dir
tar xjf archive.tar.bz2                  # extract bzip2
tar xJf archive.tar.xz                   # extract xz

# LIST contents (without extracting):
tar tvf archive.tar.gz                   # t=list, v=verbose, f=file

# tar auto-detects compression (modern versions):
tar xf archive.tar.gz    # auto-detects and extracts any compression

# zip/unzip:
zip -r archive.zip directory/            # create zip (recursive)
unzip archive.zip                        # extract
unzip -l archive.zip                     # list contents
unzip archive.zip -d /target/dir/        # extract to directory

# gzip/gunzip (single file):
gzip file.log                            # creates file.log.gz, removes original
gunzip file.log.gz                       # decompress
gzip -k file.log                         # keep original (-k)
gzip -d file.log.gz                      # decompress (same as gunzip)
zcat file.log.gz                         # view without decompressing
```

---

### First Principles

**tar flags breakdown:**
```
c = create new archive
x = extract from archive
t = list (table of) contents
f = file (next argument is the archive filename)
z = gzip compression/decompression
j = bzip2 compression/decompression
J = xz compression/decompression
v = verbose (list files being processed)
C = change to directory before operation

Memory aid:
  Create: tar c[compression]f archive.tar.gz source/
  Extract: tar x[compression]f archive.tar.gz
  List: tar t[compression]f archive.tar.gz

Modern GNU tar: auto-detects compression with 'f' alone
  tar xf anything.tar.gz    # works for all compression types
```

**Why tar separates archiving from compression:**
Unix philosophy: each tool does one thing well. tar handles:
preserving directory structure, permissions, ownership, timestamps,
symlinks, special files. Compression algorithms handle: size reduction.
Combining them is flexible: choose compression based on speed/ratio
tradeoff: gzip (fast), bzip2 (medium), xz (slow, best). Or stream
through a compressor: `tar cf - dir/ | pigz > archive.tar.gz` (parallel gzip).

---

### Thought Experiment

Application deployment package: 500 source files, 50 config files, 3
scripts. Need to ship to 10 servers.

```bash
# BAD: copy files individually
for server in server{1..10}; do
    scp -r ./myapp/ $server:/opt/
done
# 550 files x 10 servers = 5,500 individual file transfers
# rsync would be better for updates, but first deployment = archive

# GOOD: package once, ship once
tar czf myapp-v2.1.tar.gz ./myapp/
# Now deploy the single archive:
for server in server{1..10}; do
    scp myapp-v2.1.tar.gz $server:/tmp/
    ssh $server "tar xzf /tmp/myapp-v2.1.tar.gz -C /opt/ && \
                 rm /tmp/myapp-v2.1.tar.gz"
done
# 10 file transfers (not 5,500) + remote extract
# Faster, atomic per-server (all files appear at once after extraction)
```

---

### Mental Model / Analogy

tar + gzip is like **vacuum packing:**

```
Without packaging (files):
  [file1] [file2] [file3] ... [file500]
  500 separate items to move - tedious, slow

tar (archiving only):
  [=====tar archive (all 500 files inside)=====]
  One item to move, original size

tar + gzip (archiving + compression):
  [=tar.gz (all 500 files, compressed)=]
  One item, significantly smaller
  
Extraction = cut open the vacuum bag:
  tar xzf = cut open + pour out all files to their correct locations
  
zip = pre-compressed vacuum bags for each item, all in one box
     (individual items can be extracted without decompressing others)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`tar czf name.tar.gz dir/` and `tar xzf name.tar.gz`. These two cover
90% of daily use. Add `-C dir/` to control extraction location.
`tar tvf` to list contents before extracting (verify before you extract).

**Level 2:**
Compression comparison: gzip (1-3s/GB, 60% reduction), bzip2 (slower,
65% reduction), xz (slowest, 70-75% reduction). For daily backup logs:
gzip is usually right. For archiving old code/data for long-term storage:
xz. Excluding files: `tar czf archive.tar.gz dir/ --exclude='*.log'`
or `--exclude-from=.tarignore`. Append to existing: `tar rf archive.tar file`.
Incremental: `tar czf backup-$(date +%Y%m%d).tar.gz dir/ --newer=last_backup`.

**Level 3:**
Stream tar over SSH: `tar czf - dir/ | ssh user@host "tar xzf - -C /opt/"` -
no intermediate file needed, piped directly. List specific files:
`tar xzf archive.tar.gz path/to/specific/file`. Verify integrity:
`tar tzf archive.tar.gz` (lists = verifies) or `gzip -t archive.tar.gz`
(test without extracting). `--strip-components=N` removes N leading
path components on extraction.

**Level 4:**
Split archives for size-limited storage:
```bash
tar czf - dir/ | split -b 1G - backup.tar.gz.part
# Reassemble:
cat backup.tar.gz.part?? | tar xzf -
```
Parallel compression (`pigz` = parallel gzip, `pbzip2`):
`tar cf - dir/ | pigz -p 8 > archive.tar.gz` - uses 8 CPU cores.
On multi-core servers: pigz can be 4-8x faster than gzip for large files.
Docker layers are essentially tar archives with gzip compression.

**Level 5:**
Container image internals: OCI images are tar archives of tar archives.
Each Docker layer is a tar.gz. `docker save image | tar xf -` reveals
the layer structure. Artifact management: Maven/Gradle build artifacts in
Nexus/Artifactory are zips. npm packages are tar.gz. pip wheels are zips.
Understanding the archive format lets you inspect build artifacts without
specialized tools. `jar tf myapp.jar` = `unzip -l myapp.jar` (JAR files
are ZIP archives).

---

### Code Example

**BAD - unsafe extraction:**
```bash
# BAD 1: extract without checking contents first (tar bomb risk)
tar xzf downloaded-archive.tar.gz
# What if the archive contains: ../../etc/passwd or absolute paths?
# Or 1 million tiny files that fill your filesystem?

# ALWAYS list contents first:
tar tvf downloaded-archive.tar.gz | head -20
# Check: does it start with a directory name? Or bare files?
# If bare files: extract to a subdirectory to avoid contaminating cwd
tar xzf archive.tar.gz -C ./extracted/  # safe extraction location

# BAD 2: not preserving permissions when needed
tar czf backup.tar.gz /etc/myapp/
tar xzf backup.tar.gz  # extracts to /etc/myapp/ relative to cwd, not /etc/myapp/

# For absolute path restoration:
tar xzf backup.tar.gz -C /   # extract to root (preserves absolute paths)
# Note: requires root permissions to restore /etc/ files

# BAD 3: compressing already compressed files
gzip application.tar.gz  # .tar.gz is already compressed
# Creates application.tar.gz.gz - larger than the original .tar.gz
# ZIP files, JARs, PNGs, JPEGs, MP4s = already compressed = don't re-gzip
```

**GOOD - production patterns:**
```bash
# Log rotation with timestamps:
rotate_logs() {
    local log_dir="/var/log/myapp"
    local archive_dir="/var/log/archive"
    local date_suffix=$(date +%Y%m%d)
    
    mkdir -p "$archive_dir"
    
    # Archive logs older than 1 day, compress, keep for 90 days
    find "$log_dir" -name "*.log" -mtime +1 \
        -exec tar czf "${archive_dir}/logs-${date_suffix}.tar.gz" {} + \
        2>/dev/null
    
    # Delete archives older than 90 days
    find "$archive_dir" -name "*.tar.gz" -mtime +90 -delete
}

# Safe deployment extraction with backup:
deploy() {
    local archive="$1"
    local app_dir="/opt/myapp"
    local backup_dir="/opt/myapp-backup-$(date +%Y%m%d-%H%M%S)"
    
    # Verify archive before touching production
    tar tzf "$archive" > /dev/null || {
        echo "Archive corrupt or not found" >&2
        exit 1
    }
    
    # Backup current version
    if [ -d "$app_dir" ]; then
        mv "$app_dir" "$backup_dir"
    fi
    
    # Extract new version
    mkdir -p "$app_dir"
    tar xzf "$archive" -C "$app_dir" --strip-components=1
    
    echo "Deployed successfully. Backup at: $backup_dir"
}

# Streaming tar over SSH (no temp file):
# Send directory to remote server:
tar czf - ./myapp/ | ssh user@server "tar xzf - -C /opt/"
# Pull directory from remote server:
ssh user@server "tar czf - /opt/myapp/" | tar xzf - -C ./

# Create incremental backup:
LAST_BACKUP="/tmp/last_backup_timestamp"
touch -d "yesterday" "$LAST_BACKUP" 2>/dev/null || true
tar czf "incremental-$(date +%Y%m%d).tar.gz" \
    /opt/myapp/data/ \
    --newer="$LAST_BACKUP"
touch "$LAST_BACKUP"
```

---

### Compression Comparison Table

| Format | Extension | Speed | Compression | Cross-platform | Use case |
|--------|-----------|-------|-------------|----------------|----------|
| gzip | .tar.gz | Fast | Good (60%) | Unix/Linux | Standard - use this by default |
| bzip2 | .tar.bz2 | Slow | Better (65%) | Unix/Linux | When ratio > speed |
| xz | .tar.xz | Very slow | Best (70%+) | Unix/Linux | Distribution packages, long-term storage |
| zip | .zip | Fast | Good | ALL platforms | Windows interop, Java JARs |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "tar compresses files" | tar only ARCHIVES (combines) files. Compression is added by specifying z (gzip), j (bzip2), or J (xz). `tar cf archive.tar dir/` creates an UNCOMPRESSED tar. `tar czf archive.tar.gz dir/` creates a gzip-compressed tar. |
| "zip and tar.gz are the same" | zip is a combined archive+compression format where each file is independently compressed (random access possible). tar.gz compresses the entire archive as one stream (better compression, but must decompress fully to access one file). zip is standard on Windows; tar.gz is standard on Unix/Linux. |
| "Always use the highest compression" | Higher compression = slower. For daily log rotation: gzip is usually right (fast enough, reasonable ratio). For a one-time archive of old data: xz makes sense (maximum ratio, speed doesn't matter). For transferring large files over slow networks: xz. For CI/CD pipeline artifacts: gzip (speed matters). |
| "Extracting tar replaces existing files safely" | tar extracts without checking if files exist - it OVERWRITES existing files. For production deployments: extract to a temp location, then atomically move into place with `mv`, or keep a backup of the old version before extracting. |
| "gzip -9 is always best" | `-9` = maximum compression level but significantly slower. For interactive use: the default (level 6) is usually sufficient. `gzip -9` is typically only 2-5% smaller than default but 2-5x slower. Use `-1` (fastest) for temp compression that won't be kept long. |

---

### Failure Modes & Diagnosis

**"tar: Error is not recoverable" during extraction:**
```bash
# Problem: archive is corrupt
tar xzf corrupted.tar.gz
# Error: tar: Error is not recoverable

# Test: verify archive integrity
gzip -t archive.tar.gz    # tests gzip integrity
tar tzf archive.tar.gz    # lists contents (tests tar integrity too)

# Partial recovery from corrupt archive:
tar xzf corrupted.tar.gz --ignore-zeros 2>/dev/null
# Extracts what it can, ignores corrupt sections

# Prevention: verify immediately after creation
tar czf archive.tar.gz dir/ && tar tzf archive.tar.gz > /dev/null
echo "Archive verified OK"

# Or: use checksums
sha256sum archive.tar.gz > archive.tar.gz.sha256
# On receiving end:
sha256sum -c archive.tar.gz.sha256
```

**Disk fills during extraction:**
```bash
# Check archive size before extracting:
tar tzf archive.tar.gz | awk '{sum += $3} END {
    printf "Uncompressed size: %.1f MB\n", sum/1024/1024
}'

# Check available space:
df -h /target/directory

# If not enough space: extract to different volume
tar xzf archive.tar.gz -C /large/disk/path/
```

---

### Related Keywords

**Foundational:**
LNX-007 (FHS), LNX-008 (Files)

**Builds on this:**
LNX-068 (Backup and Recovery), LNX-024 (Shell Scripting)

**Related:**
LNX-025 (find - for finding files to archive), LNX-033 (disk usage)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `tar czf name.tar.gz dir/` | Create gzipped archive |
| `tar xzf archive.tar.gz` | Extract gzipped archive |
| `tar xzf archive.tar.gz -C dir/` | Extract to specific directory |
| `tar tvf archive.tar.gz` | List contents |
| `tar xf archive.tar.gz` | Auto-detect compression and extract |
| `tar czf archive.tar.gz --exclude='*.log'` | Create excluding files |
| `gzip file` | Compress single file |
| `gunzip file.gz` | Decompress single file |
| `zcat file.gz` | View compressed file without decompressing |
| `zip -r archive.zip dir/` | Create zip (recursive) |
| `unzip archive.zip -d dir/` | Extract zip to directory |
| `unzip -l archive.zip` | List zip contents |

**3 things to remember:**
1. Flags: `czf` = CREATE gzipped file; `xzf` = EXTRACT gzipped file; `tvf` = list (TABLE)
2. Always `tar tvf` before extracting untrusted archives (check for path traversal)
3. JAR files are ZIP format: `jar tf`, `jar xf`, or `unzip -l` on any JAR

---

### Transferable Wisdom

Archive + compress is the universal packaging pattern. npm publishes packages
as `.tar.gz`. pip publishes `.whl` (ZIP). Maven publishes `.jar` (ZIP).
Docker images are `.tar` archives of tar layers. Kubernetes Helm charts are
`.tar.gz`. Understanding the underlying format lets you inspect, repair, or
create these artifacts without specialized tools.

The pipeline pattern (`tar cf - src/ | ssh host "tar xf - -C /dest/"`) is
the basis for: Docker image push/pull (streaming tar over HTTP), rsync
delta streaming, Kubernetes volume backup operators. Streaming archives
over pipes avoids intermediate files - a key optimization for large datasets
and bandwidth-constrained environments.

---

### The Surprising Truth

The `tar` utility (tape archive) was literally designed for magnetic tape
drives in the 1970s. The file format has no file count or total size
header - it just concatenates file headers and data blocks until end-of-tape
markers (two 512-byte blocks of zeros). This is why `tar tvf archive.tar.gz`
must scan the entire archive to count files, and why appending to a tar
file (`tar rf`) is fast (just add to the end) but random access is slow
(must scan from the beginning). Today, tar archives are stored on SSDs,
streamed over networks, and embedded in container images - but the
format is identical to what was used with 9-track reel-to-reel tape drives
in 1979. The `.tar` file you create today would be readable by a VAX
running 4BSD in 1980 (assuming the hardware still works).

---

### Mastery Checklist

- [ ] Can create and extract tar.gz archives
- [ ] Can list archive contents before extracting
- [ ] Can choose appropriate compression (gzip vs bzip2 vs xz)
- [ ] Can use --exclude and -C options
- [ ] Can use gzip/gunzip/zcat for single file compression

---

### Think About This

1. You receive a tar.gz archive from an external source and need to
   extract it on a production server. What do you check BEFORE running
   `tar xzf` to ensure the extraction is safe and doesn't cause problems?
   What is a "tar bomb" and how do you detect one?

2. `tar czf - dir/ | ssh user@host "tar xzf - -C /opt/"` - explain
   what the `-` means in both `czf -` and `xzf -`. Why is this approach
   sometimes better than creating an intermediate file? What are its
   disadvantages?

3. You need to create a daily backup script for `/var/data` that: keeps
   compressed archives for 30 days, uses filenames with dates, and can
   be run again safely (idempotent). Write the key tar command and
   the cleanup command. What would make this NOT idempotent?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you create a gzip-compressed archive of a directory and then extract it on another server?
A: Create: `tar czf archive.tar.gz ./directory/`. Flag breakdown: `c` = create, `z` = gzip compression, `f` = next arg is filename. Transfer: `scp archive.tar.gz user@server:/tmp/`. Extract on server: `tar xzf /tmp/archive.tar.gz -C /opt/` where `x` = extract, `-C /opt/` = change to /opt before extracting. List contents without extracting: `tar tvf archive.tar.gz`. Modern GNU tar can auto-detect compression: `tar xf archive.tar.gz` works for all compression formats. One-shot over SSH without intermediate file: `tar czf - ./directory/ | ssh user@server "tar xzf - -C /opt/"`.

**Intermediate:**
Q: What is the difference between `gzip` and `bzip2` compression, and when would you choose one over the other?
A: Both compress data, but with different algorithms and tradeoffs. gzip uses DEFLATE algorithm (LZ77 + Huffman coding): fast compression/decompression, typically 60-70% size reduction on text/code, widely supported everywhere. bzip2 uses Burrows-Wheeler transform + Huffman coding: 5-15% better compression than gzip, 3-5x slower compression and 2x slower decompression, less universal. xz (LZMA2) compresses best but is slowest. Decision criteria: (1) gzip by default - it's fast, universally supported, and good enough. (2) bzip2 when you need to store archives long-term and bandwidth/storage is more precious than CPU time. (3) xz for Linux distribution packages where maximum compression is worth the CPU cost (users download once, distro compresses once). (4) For real-time streaming: gzip. For CPU-bound systems with lots of I/O: gzip. For one-time archives to cold storage: xz. Parallel alternatives: `pigz` (parallel gzip), `pbzip2` (parallel bzip2) use multiple CPU cores and are dramatically faster for large files.

**Expert:**
Q: JAR files are ZIP archives. Explain how you can inspect, modify, and repack a JAR file using standard Linux tools without the JDK jar command.
A: JAR files are standard ZIP format (defined by PKZIP, same as .zip). Standard tools that work: (1) List contents: `unzip -l myapp.jar` or `jar tf myapp.jar`. (2) Extract: `unzip myapp.jar -d extracted/` or `jar xf myapp.jar`. (3) View specific file: `unzip -p myapp.jar META-INF/MANIFEST.MF` (unzip to stdout). (4) Extract specific file: `unzip myapp.jar com/example/Config.class`. (5) Modify: extract, change files, repack: `cd extracted/ && zip -r ../myapp-modified.jar .`. (6) Add/update file: `zip myapp.jar com/example/NewFile.class` (adds/updates in-place). Production use cases: (1) Inspecting deployed JARs for version info (read MANIFEST.MF). (2) Extracting embedded config from a fat JAR. (3) Replacing a config file in a JAR without recompiling (e.g., update application.properties in a Spring Boot fat JAR). (4) Security analysis: `unzip -l suspect.jar | grep -i "backdoor\|exploit"`. Important caveat: modifying JARs may break signature verification (signed JARs in enterprise environments). The `jarsigner -verify` command checks integrity. Modified JARs need to have signatures removed or re-signed.
