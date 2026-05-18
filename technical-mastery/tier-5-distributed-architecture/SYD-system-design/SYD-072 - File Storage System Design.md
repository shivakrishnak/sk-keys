---
id: SYD-072
title: File Storage System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-070, SYD-019
used_by: ""
related: SYD-070, SYD-019, SYD-067, SYD-049, SYD-016
tags:
  - architecture
  - file-storage
  - distributed
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 72
permalink: /technical-mastery/syd/file-storage-system-design/
---

⚡ TL;DR - Design a Dropbox/Google Drive: users store
files, sync across devices, share with collaborators.
Three layers: (1) Metadata layer - file names, paths,
version history, sharing permissions (SQL database);
(2) Block storage layer - file content chunked into
4MB blocks, stored in blob storage (S3); content-
addressed (SHA-256 hash of content = block ID =
deduplication for free); (3) Sync layer - client
detects local file changes, uploads only changed
blocks, reconciles conflicts. Key insight: files are
not stored as whole objects but as lists of blocks.
A 1GB file is 256 × 4MB blocks. A 1-byte edit
uploads only the changed block (4MB), not the full
1GB file.

| #072 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Blob Storage Design, Database Replication (System) | |
| **Related:** | Blob Storage Design, Database Replication, CDN Architecture Pattern, Video Streaming Design, Horizontal Scaling | |

---

### 🔥 The Problem This Solves

Users need to: (1) store files up to 100GB; (2) sync
changes across laptop, phone, tablet; (3) share files
with collaborators; (4) view previous versions; (5) work
offline and sync when reconnected. Simple solution:
store each file as a single S3 object. Problem: every
1-byte edit re-uploads the full 100GB file. Every edit
uploads the complete file (slow, wasteful). The block-
based approach: break files into 4MB chunks. Only upload
changed chunks. 1-byte edit: upload 1 × 4MB block (max).
100GB file with 1-byte change: 4MB upload instead of 100GB.

---

### 📘 Textbook Definition

**File storage system:** A distributed system providing
file CRUD operations, versioning, sharing, and multi-
device synchronization for user files.

**Block chunking:** Splitting files into fixed-size
pieces (blocks, e.g., 4MB). Each block stored
independently. Files are stored as ordered lists of
block references (block IDs).

**Content-addressed storage (CAS):** Block ID =
cryptographic hash of block content (SHA-256). Same
content = same ID. Different content = different ID.
Uploading the same block twice: second upload is a
no-op (already exists). Deduplication is automatic.

**Delta sync:** On file update, the client computes
which blocks have changed (by comparing SHA-256 hashes).
Only changed blocks are uploaded. Unchanged blocks
already exist in storage. Reduces upload bandwidth
dramatically.

**Conflict resolution:** Two clients edit the same file
offline. Both upload conflicting versions. System must
detect and either auto-merge (for text: line-level diff)
or create a "conflict copy" for manual resolution.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Files chunked into 4MB blocks. Blocks content-addressed
(hash = ID). Only changed blocks upload on edit.
Metadata (paths, versions, sharing) in SQL.

**One analogy:**
> A book in a library system:
>
> Without chunking: every book edit reprints the entire
> book (100GB upload). Slow and expensive.
>
> With chunking: every chapter (4MB) is a separate page.
> Edit chapter 3: reprint only chapter 3. Rest are
> already on the shelf. The library catalog (metadata DB)
> records: "Book X = chapters [1, 2, 3_v2, 4, ..., 256]."
>
> Content addressing: two books with identical chapter 3
> share the same physical chapter copy on the shelf.
> Storage used only once for identical content.
> This is deduplication.

**One insight:**
Content-addressed storage gives deduplication
automatically and cheaply. If 1,000 users all upload
the same PDF (a publicly available report), you store
it once. The blocks from user A's file and user B's
file resolve to the same SHA-256 hash. Storage used: 1×,
not 1,000×. This is particularly valuable for backup
systems where users often backup the same OS files
(Windows DLLs, standard libraries) across millions
of machines.

---

### 🔩 First Principles Explanation

**ARCHITECTURE LAYERS:**
```
┌─────────────────────────────────────────────────────┐
│ LAYER 3: SYNC CLIENT (phone, laptop)               │
│ - Watch filesystem for changes                     │
│ - Chunk changed files into 4MB blocks             │
│ - Compare block hashes against server manifest    │
│ - Upload only new/changed blocks                  │
│ - Receive change notifications from server        │
└───────────────────────┬─────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼─────────────────────────────┐
│ LAYER 2: API & SYNC SERVICE                        │
│ - Auth and authorization                          │
│ - Block upload/download endpoints                 │
│ - File metadata operations (create, rename, share)│
│ - Generate presigned S3 URLs for block uploads   │
│ - Send change notifications to other devices     │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
┌──────────▼──────────┐ ┌────────▼────────────────────┐
│ METADATA DB         │ │ BLOCK STORE (S3)            │
│ (PostgreSQL)        │ │ - Keyed by block SHA-256    │
│ - users             │ │ - Immutable (never modified)│
│ - files             │ │ - Content-addressed         │
│ - file_versions     │ │ - CDN for fast downloads   │
│ - file_blocks       │ │ - Lifecycle: compress/tier │
│ - share_permissions │ └─────────────────────────────┘
└─────────────────────┘
```

**SCHEMA (simplified):**
```sql
-- File metadata (not the content)
CREATE TABLE files (
  id            BIGINT PRIMARY KEY,
  user_id       BIGINT REFERENCES users,
  parent_dir_id BIGINT REFERENCES files NULL,
  name          VARCHAR(255),
  path          TEXT,              -- materialized path
  is_directory  BOOLEAN DEFAULT false,
  created_at    TIMESTAMP,
  updated_at    TIMESTAMP
);

-- Each save creates a new version (immutable)
CREATE TABLE file_versions (
  id          BIGINT PRIMARY KEY,
  file_id     BIGINT REFERENCES files,
  version     INT,
  size_bytes  BIGINT,
  created_at  TIMESTAMP,
  -- Latest version marker
  is_current  BOOLEAN DEFAULT true
  -- Previous version: is_current=false (soft delete)
);

-- Ordered list of blocks for each version
CREATE TABLE file_version_blocks (
  version_id      BIGINT REFERENCES file_versions,
  block_seq       INT,    -- position in file
  block_id        CHAR(64),  -- SHA-256 hex
  PRIMARY KEY (version_id, block_seq)
);

-- The actual block data: in S3, keyed by SHA-256.
-- table ref for dedup tracking (optional):
CREATE TABLE blocks (
  block_id        CHAR(64) PRIMARY KEY,  -- SHA-256
  size_bytes      INT,
  reference_count INT DEFAULT 1
  -- Object key in S3: blocks/{block_id[:2]}/{block_id}
  -- (prefix sharding: /ab/abcd1234...)
);
```

**UPLOAD FLOW (delta sync):**
```
Client modifies file.txt (1GB, 256 blocks).
Block 100 changed. Blocks 0-99, 101-255 unchanged.

1. Client computes SHA-256 for each block.
2. Client sends to API: "file.txt manifest"
   [block_0_hash, block_1_hash, ..., block_255_hash]

3. API: compare against current stored manifest.
   Returns: "Need blocks: [block_100_hash]"
   (All others already in S3)

4. Client: request presigned S3 URL for block_100.
5. Client: upload block_100 directly to S3.
6. Client: POST /api/file/version/commit
   {file_id, blocks: [b0, b1, ..., b100_new, ..., b255]}

7. API:
   - INSERT file_versions (new version)
   - INSERT file_version_blocks (block list)
   - Notify other devices via WebSocket / push

8. Other devices: receive notification.
   Pull updated manifest. Download only block_100.
   Reconstruct file from existing blocks + block_100.
```

**CONFLICT RESOLUTION:**
```
User A (laptop): edits file.txt offline. Saves.
User A (phone):  edits same file.txt offline. Saves.
Both come online. Both upload new versions.

Detection:
  Laptop: uploads version 5 (parent: version 4)
  Phone:  uploads version 5 (parent: version 4)
  Server: version 5 already exists. CONFLICT.

Strategies:
  1. Last-write-wins (LWW):
     Higher timestamp = winner. Other is discarded.
     Simple but loses data. Use for non-critical data.

  2. Conflict copy:
     Both versions kept. User sees two files:
     "report.pdf" and "report (conflict copy
       2024-01-15).pdf"
     User resolves manually. Dropbox uses this.

  3. Operational transform / CRDT:
     Track individual edits. Merge at edit level.
     Used by Google Docs (not typical file storage).
     Complex to implement correctly.

Most file storage systems use conflict copies (option 2).
```

---

### 🧪 Thought Experiment

**Deduplication at Scale**

10 million users. Average file: 1GB.
Without dedup: 10 million × 1GB = 10 petabytes.
Cost at $0.023/GB: $230 million/month.

With content-addressed blocks:
- OS files (Windows, macOS): same across all users.
  1 million users on macOS: same 50GB of OS files.
  Without dedup: 50 petabytes just for OS files.
  With dedup: 50GB (1 copy shared by 1 million users).
  Savings: 50 petabytes → 50 GB. 1,000,000× reduction.
- User documents: high uniqueness (little dedup benefit).
- Backups: same files backed up repeatedly = high dedup.

Dropbox reported ~20-30% storage savings from
dedup on user files. For backup workloads (same files
across time and users), savings can exceed 80%.

---

### 🧠 Mental Model / Analogy

> A file storage system is like a LEGO bin:
>
> Files (constructs) = ordered lists of LEGO bricks.
> Blocks = individual LEGO bricks.
> Content addressing: each unique LEGO shape has a
> unique catalog number (hash). Same shape = same number.
>
> Storing a file: record which bricks (block IDs) in
> which order. The bricks go in the shared bin (S3).
> Updating a file: swap out just the changed bricks.
> Keep the rest from the shared bin (dedup).
> Sharing a file: both users' manifests point to the
> same bricks in the shared bin. One copy, two references.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
File storage systems like Dropbox store your files and
sync them across all your devices. When you change a file,
only the changed parts are uploaded - not the whole file.
This makes syncing fast. Files are stored on cloud
storage, accessible from anywhere.

**Level 2 - How to use it (junior developer):**
Use S3 for blob storage, PostgreSQL for metadata
(file names, paths, versions, permissions). Implement
chunking: split files into 4MB blocks. Upload blocks
to S3 keyed by SHA-256 hash. Store the block list in
metadata DB. Delta sync: compute block hashes locally,
ask server which are missing, upload only those.

**Level 3 - How it works (mid-level engineer):**
Content-addressed block storage: SHA-256(block) = block
key. Same content uploaded once (dedup). File version:
ordered list of block IDs. Delta sync: client sends
manifest of block hashes; server returns missing ones.
Presigned URLs: client uploads blocks directly to S3.
Conflict resolution: conflict copies for concurrent offline
edits. WebSockets/SSE for push change notifications.

**Level 4 - Why it was designed this way (senior/staff):**
Block-level deduplication is content-addressed storage
applied at the infrastructure layer. The immutability
invariant: blocks never change (content-addressed means
any change creates a new hash = new block). File
versions are snapshots (pointers to block lists), not
diffs. This means: version history is cheap storage-
wise (only changed blocks are new; unchanged blocks
are shared). Rolling back to any version: reconstruct
from block list at that version. No diff application
needed. The tradeoff: small files have overhead (each
file has at least one block, metadata entry, version).
Dropbox optimized by packing many small files into a
single large block (reducing S3 per-object overhead).

**Level 5 - Mastery (distinguished engineer):**
Dropbox's Magic Pocket (2016): moved from S3 to a
custom block storage system. Motivations: (1) S3 per-
request pricing was significant at their scale
(billions of block operations/day); (2) custom storage
allowed specialized erasure coding (reducing redundancy
from 3× replication to 1.3× with same durability);
(3) geographic placement control for compliance.
The system stores blocks using Reed-Solomon erasure
coding: a block is split into 14 fragments (9 data + 5
parity). Any 9 of 14 fragments can reconstruct the
block. Stored across 14 machines; up to 5 can fail
simultaneously without data loss. Storage overhead:
14/9 = 1.56× vs. 3× for triple replication.
This is only worth building at petabyte scale.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ FILE UPLOAD (delta sync)                            │
│                                                      │
│ Client: file.txt modified (1GB, block 100 changed) │
│                                                      │
│ 1. Compute SHA-256 for all 256 blocks              │
│ 2. POST /api/sync/check_blocks                     │
│    [hash_0, hash_1, ..., hash_255]                │
│ 3. Server: query blocks table.                    │
│    Return: [hash_100]  (only missing one)         │
│ 4. GET /api/blocks/presigned-url?block=hash_100   │
│    Server returns: presigned S3 PUT URL           │
│ 5. Client: PUT block_100 directly to S3           │
│ 6. POST /api/files/{id}/versions                  │
│    Body: {blocks: [h0, h1, ..., h100_new, h255]}  │
│ 7. Server:                                        │
│    INSERT file_versions                           │
│    INSERT file_version_blocks (all 256)           │
│    Notify other devices (WebSocket)               │
│                                                      │
│ Other devices:                                     │
│ 8. Receive notification via WebSocket             │
│ 9. POST /api/sync/check_blocks (send local hashes)│
│ 10. Server returns: [hash_100] (missing)          │
│ 11. Download block_100 from CDN                   │
│ 12. Reconstruct file from local blocks + new one  │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Block chunking and upload (Python)**
```python
import hashlib
import os
from pathlib import Path
from typing import List, Tuple

BLOCK_SIZE = 4 * 1024 * 1024  # 4MB

def chunk_file(file_path: str
               ) -> List[Tuple[int, str, bytes]]:
    """
    Split file into 4MB blocks.
    Returns: [(seq, sha256_hex, block_data), ...]
    """
    blocks = []
    path = Path(file_path)
    
    with open(path, 'rb') as f:
        seq = 0
        while True:
            data = f.read(BLOCK_SIZE)
            if not data:
                break
            block_hash = hashlib.sha256(data).hexdigest()
            blocks.append((seq, block_hash, data))
            seq += 1
    
    return blocks

def delta_sync(file_path: str,
               file_id: int,
               api_client) -> str:
    """
    Upload only changed blocks.
    Returns: new version_id
    """
    # 1. Chunk file, compute hashes
    blocks = chunk_file(file_path)
    block_hashes = [h for (_, h, _) in blocks]
    
    # 2. Ask server which blocks it needs
    needed = api_client.check_blocks(block_hashes)
    needed_set = set(needed)
    
    # 3. Upload only missing blocks (direct to S3)
    for seq, block_hash, block_data in blocks:
        if block_hash in needed_set:
            presigned = api_client.get_upload_url(
                block_hash)
            api_client.upload_block_direct(
                presigned, block_data,
                content_type="application/octet-stream"
            )
    
    # 4. Commit the new version (metadata only)
    version_id = api_client.commit_version(
        file_id=file_id,
        blocks=block_hashes  # ordered list of hashes
    )
    
    return version_id

def reconstruct_file(version_id: int,
                     output_path: str,
                     api_client,
                     block_cache: dict):
    """
    Download and reassemble a file version.
    block_cache: local disk cache of already-downloaded blocks.
    """
    # Get ordered block list from server
    block_list = api_client.get_version_blocks(version_id)
    
    with open(output_path, 'wb') as f:
        for block_hash in block_list:
            if block_hash in block_cache:
                # Already have this block locally
                data = block_cache[block_hash]
            else:
                # Download from CDN
                data = api_client.download_block(block_hash)
                block_cache[block_hash] = data
            f.write(data)
```

**Example 2 - Version listing and restore (API endpoint)**
```python
from fastapi import FastAPI, HTTPException, Depends

@app.get("/api/files/{file_id}/versions")
async def list_versions(file_id: int,
                        current_user = Depends(auth)):
    """List all versions of a file"""
    # Check read access
    file = db.query_one(
        "SELECT * FROM files WHERE id = %s",
        [file_id])
    if not file:
        raise HTTPException(status_code=404)
    check_read_access(current_user, file)
    
    versions = db.query(
        "SELECT v.id, v.version, v.size_bytes, "
        "v.created_at "
        "FROM file_versions v "
        "WHERE v.file_id = %s "
        "ORDER BY v.version DESC "
        "LIMIT 50",
        [file_id]
    )
    return {"versions": versions}

@app.post("/api/files/{file_id}/restore")
async def restore_version(
        file_id: int,
        version_id: int,
        current_user = Depends(auth)):
    """
    Restore a file to a previous version.
    Creates a new version (does not delete history).
    """
    # Get the block list for the target version
    target_blocks = db.query(
        "SELECT block_id FROM file_version_blocks "
        "WHERE version_id = %s "
        "ORDER BY block_seq",
        [version_id]
    )
    
    # Create a new version with the restored block list
    # (not overwrite: preserve audit trail)
    with db.transaction():
        # Mark current version as not-current
        db.execute(
            "UPDATE file_versions SET is_current=false "
            "WHERE file_id = %s AND is_current=true",
            [file_id]
        )
        
        # Get next version number
        latest = db.query_one(
            "SELECT MAX(version) as v "
            "FROM file_versions WHERE file_id=%s",
            [file_id]
        )
        new_version_num = (latest['v'] or 0) + 1
        
        # Insert new version (restored)
        new_version_id = db.execute(
            "INSERT INTO file_versions "
            "(file_id, version, is_current, "
            " restored_from_version) "
            "VALUES (%s, %s, true, %s) RETURNING id",
            [file_id, new_version_num, version_id]
        )
        
        # Copy block list from target version
        for seq, block in enumerate(target_blocks):
            db.execute(
                "INSERT INTO file_version_blocks "
                "(version_id, block_seq, block_id) "
                "VALUES (%s, %s, %s)",
                [new_version_id, seq, block['block_id']]
            )
    
    return {"new_version_id": new_version_id}
```

---

### ⚖️ Comparison Table

| Design Decision | Option A | Option B | Recommendation |
|---|---|---|---|
| **Block size** | 512KB (small, more dedup) | 8MB (large, less metadata) | 4MB (balance) |
| **Block ID** | Sequential UUID | SHA-256 of content | SHA-256 (enables dedup) |
| **Conflict resolution** | Last-write-wins | Conflict copy | Conflict copy (no data loss) |
| **Version retention** | All versions forever | Last N versions | Policy-based (30 days default) |
| **Block store** | Custom CAS | S3 | S3 (unless petabyte+ scale) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Store files as single S3 objects | This works for simple blob storage but fails for a sync system. Uploading a 1-byte change to a 100GB file re-uploads the entire 100GB. Block-based storage ensures only changed 4MB blocks are transferred. Additionally, single-object storage cannot support partial file reconstruction for streaming or resumable downloads without range requests. |
| Conflict resolution is automatic | True conflict resolution (both users edited the same part of the same file offline) is fundamentally impossible to do automatically without user intervention for binary files. Google Docs can auto-merge because it tracks individual keystrokes as operations (OT/CRDT). Dropbox treats files as opaque binary blobs - it cannot merge a conflict in a PDF or Excel file automatically. Conflict copies are the pragmatic solution. |
| Deduplication requires duplicate file detection | Content-addressed storage deduplicates at the block level automatically - you don't need to know if files are "duplicates" at the file level. If two completely different files share one identical 4MB block (e.g., both start with the same header), that block is stored once. Deduplication is a side effect of the content-addressing mechanism, not a separate system. |

---

### 🚨 Failure Modes & Diagnosis

**Sync Loop: Infinite Upload-Download Cycle**

**Symptom:**
Client is stuck in a loop: uploads a file, receives
a change notification, downloads the file, which
triggers a file system change event, which triggers
another upload. Network usage: 100% on client.
CPU: elevated. Upload never completes cleanly.

**Root Cause:**
File system watcher detects download as a change event.
The sync client treats it as a new local edit.
Computes hashes: same as what was just downloaded.
Uploads: server has same blocks. Creates new version.
Triggers another change notification. Loop.

**Fix:**
```python
# Sync client: suppress events for files being
# actively downloaded (in-flight marker)

class SyncEngine:
    def __init__(self):
        self.in_flight_downloads = set()
    
    def download_file(self, file_path: str,
                      version_id: int):
        try:
            # Mark as in-flight before writing
            self.in_flight_downloads.add(file_path)
            reconstruct_file(
                version_id=version_id,
                output_path=file_path,
                api_client=self.api,
                block_cache=self.block_cache
            )
        finally:
            # Remove marker only after write is complete
            # and FS events have settled (small delay)
            import time; time.sleep(0.5)
            self.in_flight_downloads.discard(file_path)
    
    def on_fs_change(self, file_path: str):
        if file_path in self.in_flight_downloads:
            # This change was caused by our own download.
            # Ignore it.
            return
        # Otherwise: it's a genuine user edit. Sync it.
        self.upload_changed_file(file_path)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Blob Storage Design` - file storage uses blob
  storage (S3) as its block store layer
- `Database Replication (System)` - metadata DB
  replication for availability of file metadata

**Builds On This (learn these next):**
- `CDN Architecture Pattern` - serve file downloads
  via CDN for popular files (immutable blocks)
- `Video Streaming Design` - video files are stored
  similarly; streaming adds adaptive bitrate on top
- `Horizontal Scaling` - metadata DB and API tier
  both need horizontal scaling strategies

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ BLOCKS      │ 4MB chunks, SHA-256 hash = ID.            │
│             │ Immutable. Same content = same ID = dedup.│
├─────────────┼──────────────────────────────────────────┤
  │
│ DELTA SYNC  │ Send hashes. Server returns missing ones. │
│             │ Upload only new/changed blocks.          │
├─────────────┼──────────────────────────────────────────┤
  │
│ METADATA    │ PostgreSQL: files, versions, block lists. │
│             │ Block content: S3 (keyed by SHA-256).    │
├─────────────┼──────────────────────────────────────────┤
  │
│ VERSIONS    │ Each save = new version (immutable).     │
│             │ Restore = create new version from old.  │
├─────────────┼──────────────────────────────────────────┤
  │
│ CONFLICTS   │ Two offline edits: create conflict copy. │
│             │ User resolves manually.                  │
├─────────────┼──────────────────────────────────────────┤
  │
│ UPLOAD PATH │ Presigned URL → client → S3 direct.     │
│             │ API server: metadata only.              │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Chunk → SHA-256 → delta sync.          │
│             │  SQL metadata + S3 blocks + CDN."      │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ Email System Design                       │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Files are stored as ordered lists of 4MB blocks.
   Each block keyed by SHA-256(content). Same content
   = same key = automatic deduplication. This is content-
   addressed storage. Delta sync: send hashes of local
   blocks, server returns only the missing ones to upload.
2. Two separate data stores: metadata (PostgreSQL with
   files/versions/block-lists) and block data (S3 keyed
   by SHA-256). The API server handles metadata; clients
   upload/download blocks direct to S3 via presigned URLs.
3. Conflict resolution for file storage: create a conflict
   copy (both versions preserved, user resolves manually).
   Binary files cannot be auto-merged. Only text files
   with line-level diff (like Google Docs' OT algorithm)
   support automatic merge.

**Interview one-liner:**
"File storage (Dropbox/Google Drive): chunked blocks (4MB) keyed by SHA-256 (content-
addressed = automatic deduplication). Delta sync: client sends block hashes, server
returns missing ones, client uploads only changed blocks directly to S3 via presigned
URLs. Metadata: PostgreSQL (files, versions, ordered block lists). Version history:
each save is a new immutable version (block list snapshot). Conflicts: create conflict
copy (two versions for user to resolve). Change notifications: WebSocket to other
devices. Restore: create new version from old version's block list."
