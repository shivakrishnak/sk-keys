---
layout: default
title: "SCP / rsync"
parent: "Linux"
nav_order: 139
permalink: /linux/scp-rsync/
number: "0139"
category: Linux
difficulty: ★☆☆
depends_on: SSH, Linux File System Hierarchy, Shell (bash, zsh)
used_by: CI/CD, Shell Scripting, Cron Jobs
related: SSH, curl / wget, tar / gzip / zip
tags:
  - linux
  - networking
  - devops
  - foundational
---

# 139 — SCP / rsync

⚡ TL;DR — `scp` copies files securely over SSH in a single shot; `rsync` copies only the changed parts, making it fast for large or repeated transfers.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Deploying a website update means copying 500 MB of static assets to a web server. If you use FTP, the transfer is unencrypted and transfers all 500 MB every time — even when only 3 HTML files changed. Compressing the archive first helps but now you need to unpack on the server, clean old files, and handle partial failures manually.

**THE BREAKING POINT:**
Your deployment script copies a 2 GB media directory nightly to a backup server. Network costs are running unexpectedly high. The script runs for 40 minutes and if it's interrupted, you get a half-updated directory that's inconsistent. You have no idea which files differ between source and destination.

**THE INVENTION MOMENT:**
This is exactly why `rsync` was created. Its delta-transfer algorithm computes checksums of file blocks and only transmits the differences — shrinking a 2 GB nightly sync to transmitting only the 10 MB that changed, in 30 seconds.

---

### 📘 Textbook Definition

`scp` (Secure Copy) is a command-line utility that copies files between hosts over an SSH connection. It provides encryption and authentication but transfers files entirely without delta compression. `rsync` (Remote Sync) is a file synchronisation tool that uses the rsync algorithm: it divides files into fixed-size blocks, computes checksums for each block on source and destination, and transmits only the blocks that differ. Both tools use SSH as the transport layer by default.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`scp` is a secure copy command; `rsync` is a smart sync that sends only what changed.

**One analogy:**

> `scp` is like shipping a whole bookcase to a new apartment — you pack every book regardless of whether your friend already has copies. `rsync` is like a librarian who checks which books your friend already has (correct edition), packages only the new and changed books, and sends exactly those.

**One insight:**
`rsync` doesn't just save bandwidth — its `--checksum` mode compares content fingerprints regardless of timestamp, making it idempotent: running it twice produces the same result with no wasted work the second time.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Files must be transferred securely (SSH tunnel).
2. For large or repeated transfers, full re-copy wastes bandwidth proportional to unchanged data.
3. Delta transfer requires computing a diff between remote and local state without transferring the full remote file.

**DERIVED DESIGN:**
The rsync algorithm (Andrew Tridgell, 1996) solves the "remote diff" problem without round-tripping file content:

1. The _receiver_ divides its copy into fixed blocks and sends checksums (weak: Adler-32, strong: MD5) to the _sender_.
2. The _sender_ scans its version using a rolling checksum, finding blocks that match the receiver's checksums.
3. The sender transmits only: the non-matching blocks (true changes) + instructions for assembling them with matching blocks.

This means the bandwidth scales with the size of changes, not the size of the file.

**THE TRADE-OFFS:**
**Gain:** Dramatically reduced bandwidth and time for large repeated transfers; atomic directory sync.
**Cost:** rsync requires the rsync binary on both sides, has more complex flag semantics, and the initial scan can be CPU-intensive for directories with millions of small files.

---

### 🧪 Thought Experiment

**SETUP:**
You have a 10 GB VM disk image file on Server A. One megabyte of data changed in the middle of the file. You need to copy the updated image to Server B.

**WHAT HAPPENS WITH `scp`:**
scp reads all 10 GB from Server A and writes all 10 GB to Server B. Transfer time at 100 Mbps: ~800 seconds (13+ minutes). The full file is retransmitted even though only 0.01% changed.

**WHAT HAPPENS WITH `rsync`:**
rsync computes rolling checksums for 10 GB of blocks. It identifies that only 1 MB worth of blocks differ. It transmits: 1 MB of changed blocks + metadata for reconstruction. Transfer time: under 10 seconds. The 10 GB image on Server B is updated correctly with minimal data movement.

**THE INSIGHT:**
The key insight is that the checksum comparison happens _locally_ on each side — neither side needs to send file content for the comparison phase. Only the differences travel over the wire. This separates "what is different" (local computation) from "transfer the difference" (network work).

---

### 🧠 Mental Model / Analogy

> rsync is like a smart moving company with a manifest system. Before moving, the movers photograph every item with a label at the destination. At the source, they check the manifest: if an item's photo (checksum) matches, they leave it. Only new and changed items get packed and shipped. The move is minimal, fast, and the destination ends up identical to the source.

- "Photo of every item" → checksum of each file block
- "Checking the manifest" → rolling checksum comparison
- "Only new/changed items shipped" → delta transfer
- "Destination identical to source" → rsync's guarantee

Where this analogy breaks down: rsync transfers at the byte/block level within files, not just whole files — it can partially update a large file, which a physical moving company cannot do.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`scp` copies files from one computer to another securely (like a secure version of copy-paste between machines). `rsync` does the same but is much smarter — it looks at what's already at the destination and only copies what changed, making repeated copies much faster.

**Level 2 — How to use it (junior developer):**
`scp file.txt user@server:/path/` copies a file to a remote server. `scp -r dir/ user@server:/path/` copies a directory recursively. For `rsync`: `rsync -avz localdir/ user@server:/remotedir/` syncs a directory (preserving attributes, verbose, compressed). The trailing slash on source matters: `localdir/` means "contents of", `localdir` means "the directory itself".

**Level 3 — How it works (mid-level engineer):**
`scp` launches an SSH connection and uses the SCP protocol (a simple extension of the SSH transport) to copy file data in a single stream. `rsync` also uses SSH as transport but runs an rsync daemon on the remote side, which performs the checksum exchange. The `--delete` flag removes files at destination that no longer exist at source — critical for deployments but dangerous without careful testing. `rsync` is nearly atomic at the directory level when combined with `--link-dest` (hard-link-based incremental backups).

**Level 4 — Why it was designed this way (senior/staff):**
The rsync algorithm's brilliance is solving the "remote diff" without requiring the full content of both files to be at the same location. The rolling checksum (Adler-32) allows linear scanning of the source file, matching receiver block checksums without re-scanning — O(n) in file size. `scp` is being deprecated by OpenSSH (use `sftp` or `rsync` instead) because the SCP protocol has security design flaws: it trusts the remote side to not send unexpected files, which is exploitable.

---

### ⚙️ How It Works (Mechanism)

**rsync delta algorithm:**

```
┌─────────────────────────────────────────────┐
│  RSYNC DELTA TRANSFER ALGORITHM             │
└─────────────────────────────────────────────┘

RECEIVER (Server B):
  1. Split destination file into fixed blocks (700B)
  2. Compute weak checksum (Adler-32) per block
  3. Compute strong checksum (MD5) per block
  4. Send checksum list to sender

SENDER (Server A):
  5. Scan source file with rolling window
  6. At each position: compute rolling Adler-32
  7. If weak match found: verify with MD5
  8. If both match: block is same → skip
  9. If no match: this is new/changed data

TRANSMISSION:
  10. Send changed bytes + references to matching blocks
  11. Receiver reconstructs file using:
      - Received new bytes (deltas)
      - Its own unchanged blocks (referenced by index)
```

**Key scp commands:**

```bash
# Copy local file to remote server
scp file.txt user@server:/home/user/

# Copy remote file to local
scp user@server:/path/file.txt ./local/

# Copy entire directory recursively
scp -r mydir/ user@server:/home/user/

# Copy with specific SSH key
scp -i ~/.ssh/deploy_key file.txt user@server:/tmp/

# Copy between two remote servers
scp user1@server1:/file.txt user2@server2:/dest/
```

**Key rsync commands:**

```bash
# Basic sync (dry run first!)
rsync -avzn localdir/ user@server:/remotedir/
# -a = archive (preserves permissions, timestamps, symlinks)
# -v = verbose
# -z = compress during transfer
# -n = dry-run (remove -n to actually run)

# Sync with delete (mirror)
rsync -avz --delete localdir/ user@server:/remotedir/

# Exclude patterns
rsync -avz \
  --exclude='*.log' \
  --exclude='.git/' \
  localdir/ user@server:/remotedir/

# Incremental backup with hard links (space-efficient)
rsync -avz --link-dest=/backup/yesterday \
  /data/ /backup/today/

# Show progress for large transfers
rsync -avz --progress bigfile.tar user@server:/data/

# Bandwidth throttle (in KB/s)
rsync -avz --bwlimit=5000 localdir/ user@server:/dest/
```

**rsync vs scp trailing slash behaviour:**

```bash
# rsync source trailing slash = "contents of"
rsync -av src/  server:/dst/   # src/a.txt → /dst/a.txt

# No trailing slash = "the directory itself"
rsync -av src   server:/dst/   # src/a.txt → /dst/src/a.txt
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  RSYNC TRANSFER FLOW                        │
└─────────────────────────────────────────────┘

 Developer: rsync -avz src/ user@server:/dst/
       │
       ▼
 SSH connection established to server
       │
       ▼
 rsync daemon spawned on server
       │
       ▼
 File list comparison (checksums)   ← YOU ARE HERE
       │
       ▼
 Delta computed: only changed blocks
       │
       ▼
 Changed data transferred (compressed)
       │
       ▼
 Destination files updated atomically
       │
       ▼
 Transfer summary: bytes sent/received
```

**FAILURE PATH:**
Network interruption mid-transfer → rsync can resume where it left off with `--partial`. Destination files are not corrupted because rsync writes to a temp file and atomically renames when complete.

**WHAT CHANGES AT SCALE:**
At scale (petabyte data lakes), rsync is too slow — it must scan every file for the checksum comparison. Enterprise alternatives (Rclone, AWS DataSync, Apache DistCp) use object storage metadata and parallel transfer workers to handle billions of files.

---

### 💻 Code Example

**Example 1 — BAD: deployment that copies everything every time:**

```bash
# BAD — transfers all 500MB every deploy, slow and fragile
scp -r ./build/ deploy@prod:/var/www/html/
```

**Example 1 — GOOD: rsync deployment with safety checks:**

```bash
# GOOD — dry run first to verify what will change
rsync -avzn --delete \
  --exclude='.git' \
  ./build/ deploy@prod:/var/www/html/

# If dry run looks correct, remove -n to deploy
rsync -avz --delete \
  --exclude='.git' \
  ./build/ deploy@prod:/var/www/html/
```

**Example 2 — Incremental backup strategy:**

```bash
#!/bin/bash
# Space-efficient daily backup using hard links
DATE=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

rsync -avz \
  --link-dest="/backup/${YESTERDAY}" \
  /data/ \
  "/backup/${DATE}/"

# Result: today's backup uses hard links to yesterday's
# unchanged files — only changed files use new disk space
```

**Example 3 — Rsync over non-standard SSH port:**

```bash
# SSH running on port 2222
rsync -avz -e "ssh -p 2222" \
  localdir/ user@server:/remotedir/
```

---

### ⚖️ Comparison Table

| Tool      | Delta Transfer    | Encryption     | Resumable         | Best For                      |
| --------- | ----------------- | -------------- | ----------------- | ----------------------------- |
| **rsync** | Yes (block-level) | Via SSH        | Yes (--partial)   | Repeated large syncs, backups |
| scp       | No (full copy)    | SSH native     | No                | Simple one-off secure copies  |
| sftp      | No                | SSH native     | Yes (interactive) | Interactive file browsing     |
| FTP       | No                | No (plaintext) | Depends           | Legacy; avoid                 |
| aws s3 cp | Multipart         | HTTPS          | Multipart         | S3 ↔ local transfers          |

How to choose: use `rsync` for repeated syncs and deployments (always better than `scp` for non-trivial use cases); use `scp` only for quick one-off secure copies between machines you trust; never use FTP.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                             |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| rsync trailing slash doesn't matter          | It critically changes what is synced — `src/` syncs contents, `src` syncs the directory itself into the destination |
| rsync --delete is safe to skip in production | Without --delete, removed files at source accumulate at destination; deployments become inconsistent over time      |
| scp and rsync are equally secure             | scp has known protocol vulnerabilities; OpenSSH's own man page recommends using sftp or rsync over SSH instead      |
| rsync always uses a network connection       | rsync works between local directories too — useful for local backups with delta efficiency                          |
| rsync is only useful for backups             | rsync is the standard tool for deploying static websites, syncing configuration, and build artifact distribution    |

---

### 🚨 Failure Modes & Diagnosis

**Accidental Deletion with --delete**

**Symptom:**
Destination directory suddenly loses files that should be there.

**Root Cause:**
`rsync --delete` was run with the source pointing to the wrong directory, or the source was accidentally empty.

**Diagnostic Command:**

```bash
# Always dry-run first
rsync -avzn --delete src/ user@server:/dst/
# Check output before removing the -n flag
```

**Fix:**
Restore from backup. The deleted files can only be recovered if you have a backup or snapshot.

**Prevention:**
Always run with `-n` first; use `--backup` to move deleted files to a backup directory instead of deleting them.

---

**Permission Denied on Destination**

**Symptom:**
`rsync: mkstemp ".file.XXXXXX" failed: Permission denied (13)`

**Root Cause:**
The SSH user does not have write permission on the destination directory.

**Diagnostic Command:**

```bash
# Check permissions on destination
ssh user@server 'ls -la /path/to/dest'
```

**Fix:**

```bash
# Fix directory permissions
ssh user@server 'sudo chown user:user /path/to/dest'
```

**Prevention:**
Test SSH connection and write access before adding to deployment scripts.

---

**rsync Process Left Running (Stale Lock)**

**Symptom:**
Second rsync invocation fails or the destination appears to be in an incomplete state.

**Root Cause:**
A previous rsync was killed mid-transfer, leaving partial temp files (`.FILENAME.XXXXXX`).

**Diagnostic Command:**

```bash
# Find stale rsync temp files on destination
ssh user@server 'find /dst -name ".*" -name "*.??????" -type f'
```

**Fix:**

```bash
# Remove stale temp files
ssh user@server 'find /dst -name ".*" -name "*.??????" -delete'
```

**Prevention:**
Use `--partial-dir=.rsync-partial` to collect temp files in a known location, making cleanup easier.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SSH` — both scp and rsync use SSH as their transport and authentication layer
- `Linux File System Hierarchy` — source and destination paths follow Linux filesystem conventions
- `Shell (bash, zsh)` — these are shell commands used in scripts and interactive sessions

**Builds On This (learn these next):**

- `CI/CD` — rsync is a common deployment mechanism for static files and build artifacts
- `Cron Jobs` — automated rsync jobs run on cron schedules for backups and syncs
- `Shell Scripting` — rsync is embedded in shell scripts for automated backup solutions

**Alternatives / Comparisons:**

- `curl / wget` — for downloading single files from HTTP/FTP; not for host-to-host sync
- `sftp` — interactive SSH-based file transfer with browsing, no delta compression
- `tar / gzip / zip` — archive creation for batch transfer, not incremental sync

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Secure file copy (scp) and smart delta    │
│              │ sync (rsync) over SSH                     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Full file re-copy wasted bandwidth on     │
│ SOLVES       │ repeated large transfers                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ rsync trailing slash matters:             │
│              │ src/ = contents; src = the dir itself     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Deploying static sites, backing up        │
│              │ servers, syncing build artifacts          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Syncing billions of small files           │
│              │ (overhead dominates; use object storage)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Bandwidth efficiency vs CPU cost of       │
│              │ checksum computation on both sides        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A moving company that only moves         │
│              │  what actually changed"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CI/CD deploys → Rclone → AWS DataSync    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team uses `rsync --delete` to deploy a React build to a CDN origin server. The build pipeline has a bug that occasionally produces an empty `build/` directory. Trace what happens when `rsync --delete` runs with an empty source, what the user impact is, and design a safeguard that prevents this scenario without removing the `--delete` flag from production deployments.

**Q2.** rsync uses checksums to determine what changed. An attacker with access to a backup server modifies a backup file's content but resets its modification timestamp and size to match the original. Will `rsync` detect this change by default, and what flag or alternative approach would be required to detect it? What are the performance trade-offs of that approach?
