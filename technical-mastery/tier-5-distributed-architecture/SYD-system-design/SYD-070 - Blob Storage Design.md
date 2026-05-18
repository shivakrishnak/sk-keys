---
id: SYD-070
title: Blob Storage Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-008
used_by: ""
related: SYD-008, SYD-049, SYD-067, SYD-015, SYD-072
tags:
  - architecture
  - blob-storage
  - object-storage
  - design
  - intermediate
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/syd/blob-storage-design/
---

⚡ TL;DR - Blob (Binary Large Object) storage is a
flat-namespace, key-value object store for unstructured
data: images, videos, PDFs, backups, ML model weights.
A blob has a key (URL path), binary data, and metadata.
No directory hierarchy (flat or simulated-hierarchy).
Core design: write-once-read-many, immutable objects.
Key decisions: (1) presigned URLs - let clients upload/
download directly without routing through your app server;
(2) CDN in front of blob store for reads (objects are
immutable = perfect CDN cache candidate); (3) multipart
upload for files > 5MB; (4) lifecycle policies to
automatically delete/archive old objects.

| #070 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | URL Shortener Design (object store concepts) | |
| **Related:** | URL Shortener Design, Video Streaming Design, CDN Architecture Pattern, Distributed File System, File Storage System Design | |

---

### 🔥 The Problem This Solves

Your application allows users to upload profile photos.
Native approach: store photos on the app server's
filesystem, serve via app server. Problems: (1) Multiple
app instances: uploads go to one instance, other instances
can't serve those files. (2) Disk space grows without
bound. (3) App server bandwidth consumed serving static
files (inefficient). (4) No durability guarantees.
Blob storage solution: upload to S3/GCS/Azure Blob.
Served via CDN. Infinitely scalable. 99.999999999%
durability. App server not involved in file serving.

---

### 📘 Textbook Definition

**Blob storage / Object storage:** A storage architecture
that manages data as objects (blobs) in a flat namespace
rather than a hierarchical file system. Each object
has: a unique key (identifier), binary data (content),
and metadata (content-type, size, custom attributes).

**Bucket:** The top-level container in blob storage.
Analogous to a domain or root directory. Globally unique
name (or unique within an account). Objects are stored
inside buckets.

**Object key:** The unique identifier for an object
within a bucket. Looks like a path (`images/user-123/avatar.jpg`)
but is just a string key (no real directory hierarchy).
The `/` is a convention for organizational display only.

**Presigned URL:** A temporary URL with an embedded
cryptographic signature that grants time-limited
access to upload or download a specific object.
Allows clients to access blob storage directly without
routing through the app server.

**Multipart upload:** Breaking a large file into chunks,
uploading each chunk independently (in parallel), then
completing the upload by assembling the chunks. Required
for files > 5GB on S3; recommended for > 5MB.

**Storage class / tier:** Blob storage offers multiple
tiers at different cost/access tradeoffs:
- Hot (S3 Standard): frequent access, higher cost.
- Cool (S3 Infrequent Access): lower storage cost,
  retrieval fee.
- Cold (S3 Glacier): archival, very low cost,
  minutes-to-hours retrieval time.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
S3-style key-value store for binary files.
Upload once, read via CDN. App server not in the
data path for serving files.

**One analogy:**
> A post office box system:
>
> Without blob storage: you store letters in your
> apartment (app server). When guests want a letter,
> they come to your apartment to get it (bandwidth
> consumed, you must be home).
>
> With blob storage: letters go to a P.O. Box (blob
> store). Anyone can retrieve their letter with the
> right access code (presigned URL). The post office
> is always available, has infinite boxes, and you're
> not involved in every pickup.
>
> With CDN: copies of popular letters are put in
> post offices near every city. No round-trip to
> the central P.O. Box needed.

**One insight:**
The presigned URL pattern is the most important
architectural pattern in blob storage design.
Instead of: client → app server → blob store → app server → client (2× bandwidth, app server in hot path).
Use: client → POST /upload-request → app server (returns presigned URL) → client uploads direct to S3 → client sends object key to app server (save metadata to DB).
Result: app server never handles binary data. Eliminates network bottleneck. Handles files of any size without memory pressure on app servers.

---

### 🔩 First Principles Explanation

**HOW BLOB STORAGE WORKS:**
```
S3 Architecture (simplified):

Bucket: "my-app-uploads"

Object:
  Key: "images/users/123/avatar-v3.jpg"
  Data: [binary bytes, 128KB]
  Metadata:
    Content-Type: image/jpeg
    Content-Length: 131072
    Last-Modified: 2024-01-15T10:30:00Z
    ETag: "d41d8cd98f00b204e9800998ecf8427e"
    x-amz-meta-user-id: "123"
    x-amz-meta-original-filename: "selfie.jpg"

Operations:
  PUT /bucket/key - upload object (atomic, whole object)
  GET /bucket/key - download object
  DELETE /bucket/key - remove object
  LIST /bucket?prefix=images/users/123/ - list objects
  HEAD /bucket/key - get metadata without downloading
  
Immutability: objects are replaced (new version),
not modified in-place. Each PUT is atomic.
```

**PRESIGNED URL FLOW:**
```
UPLOAD FLOW (recommended):

Client → App API: POST /api/upload/request
  Body: {filename: "photo.jpg", type: "image/jpeg"}
  
App API:
  1. Validate: file type allowed? User authenticated?
  2. Generate object key:
     "uploads/{user_id}/{uuid}.jpg"
  3. Call S3 API: generate presigned PUT URL
     (expires in 5 minutes)
  4. Return to client: {upload_url, object_key}
  
Client → S3 directly: PUT {upload_url}
  Body: binary file data
  Headers: Content-Type: image/jpeg
  
Client → App API: POST /api/upload/complete
  Body: {object_key, filename}
  
App API:
  1. Verify object exists in S3 (HEAD request)
  2. Store object_key in database (users.avatar_key)
  3. Trigger async: resize/compress image (Lambda/worker)
  4. Return: success

Benefits:
  App server never handles binary data.
  File size limited only by S3 (5TB per object).
  Client uploads at full network speed (not proxied).
  App server handles only metadata (JSON, tiny).

DOWNLOAD FLOW (public files with CDN):

Database: user.avatar_url = 
  "https://cdn.example.com/uploads/123/abc.jpg"
  
Client: GET https://cdn.example.com/uploads/123/abc.jpg
CDN: cache hit → serve from edge (< 5ms, 0 cost).
CDN: cache miss → fetch from S3 → cache at edge.
App server: not in the path at all.

DOWNLOAD FLOW (private files with presigned URL):

App API: GET /api/files/{file_id}
  1. Verify user is authorized to access file.
  2. Generate presigned GET URL (expires in 15 min).
  3. Return {download_url: "https://s3.../...?X-Amz-..."}.
  
Client → presigned URL: GET directly from S3.
S3: verifies signature → serves file directly.
App server: not in the binary data path.
```

**MULTIPART UPLOAD:**
```
For large files (> 5MB recommended, required for > 5GB):

1. InitiateMultipartUpload
   → S3 returns upload_id

2. UploadPart (for each chunk, in parallel):
   Part 1: bytes 0-5MB      → S3 returns ETag-1
   Part 2: bytes 5-10MB     → S3 returns ETag-2
   Part 3: bytes 10-15MB    → S3 returns ETag-3
   (Up to 10,000 parts, max 5GB each)

3. CompleteMultipartUpload
   → Send list of [{part_number, etag}]
   → S3 assembles file atomically
   → Returns final object ETag

Benefits:
  Parallelism: each part uploads simultaneously.
  Resumability: failed part can be retried individually.
  Large file support: required for > 5GB.

Abort: if upload fails/is abandoned, call
AbortMultipartUpload to clean up partially uploaded
parts (or set S3 lifecycle rule to auto-abort after N days
for incomplete multipart uploads - easy cost saving).
```

---

### 🧪 Thought Experiment

**Without vs. With Presigned URLs**

10,000 concurrent user photo uploads.
Each photo: 5MB.

WITHOUT presigned URLs (naive):
  Client → App server → (receive 5MB) → S3 PUT → done.
  App server bandwidth: 10,000 × 5MB = 50GB in flight.
  App server RAM: 10,000 × 5MB = 50GB buffers.
  App server: exhausted. Memory OOM. Server crashes.

WITH presigned URLs:
  App server receives: JSON request (< 1KB each).
  App server generates: presigned URL (< 1ms).
  Client: uploads directly to S3 (10,000 in parallel).
  App server: handles 10,000 × 1KB = 10MB total.
  S3: handles 50GB in parallel (designed for this).
  App server RAM: ~1MB (JSON metadata only).

Conclusion: presigned URLs reduce app server load
by 50,000× for file upload traffic. Essential for
any production file upload system.

---

### 🧠 Mental Model / Analogy

> Blob storage is like a public digital locker room:
>
> Each locker (object) has a unique number (object key).
> You can put anything in it (any binary data).
> You get a time-limited code (presigned URL) to
> open a specific locker. Give the code to a friend
> (client): they access the locker directly. You
> (app server) don't need to carry the contents back
> to them. CDN: popular locker contents are photocopied
> and stored in nearby locker rooms (edge nodes) so
> the friend doesn't travel to the central facility.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Blob storage (like Amazon S3) is a cloud service for
storing any type of file (images, videos, documents).
You upload a file, get a URL to access it. It scales
automatically - you can store 1 file or 1 trillion files
with the same API. Much simpler and cheaper than
managing your own file servers.

**Level 2 - How to use it (junior developer):**
Use AWS SDK to upload files to S3 buckets. Set ACL
to private (never public unless explicitly needed).
Generate presigned URLs for client uploads/downloads.
Store the S3 object key in your database (not the full URL).
Put CloudFront in front of S3 for reads. Set lifecycle
rules to expire/archive old objects automatically.

**Level 3 - How it works (mid-level engineer):**
Presigned URL upload flow: client requests presigned PUT
URL from app API, uploads directly to S3, notifies app
of completion (app stores metadata). For large files:
multipart upload (parallel parts, resumable). CDN for
reads: S3 bucket as CloudFront origin, TTL = 1 year
for immutable files (versioned by filename/UUID).
Lifecycle: S3 Standard → S3 IA after 30 days → Glacier
after 90 days → delete after 7 years.

**Level 4 - Why it was designed this way (senior/staff):**
S3's flat-namespace design (no real directories) was
intentional. True directory hierarchies require metadata
operations that become bottlenecks at scale (listing
a directory with millions of files). S3's flat namespace
with prefix-based listing scales horizontally: the
storage cluster can shard by key prefix across thousands
of nodes without any single node being a hot spot for
directory metadata. The `/` in object keys is purely
cosmetic - `images/user-123/photo.jpg` and
`images/user-456/photo.jpg` are independent entries
with no shared directory node. S3 achieved 99.999999999%
durability (11 nines) through synchronous replication
across 3 AZs on every PUT before acknowledging success.

**Level 5 - Mastery (distinguished engineer):**
Dropbox's 2022 migration from "Magic Pocket" (their
custom distributed storage) to a hybrid with S3 for
cold storage revealed key insights about cost optimization
at exabyte scale. S3 per-request costs (GET, PUT) are
negligible at small scale but dominate at billions of
requests per day. Dropbox reduced costs by: (1) batching
small files into larger blobs (packing), reducing
per-object overhead and S3 requests; (2) content-based
deduplication - identify duplicate content by SHA-256
hash, store once, reference many times (vast savings
for backup use cases where identical files exist across
users); (3) tiering: detect access patterns and migrate
cold objects to Glacier after 90 days of no access.
For interview purposes: blob storage design at scale
is fundamentally a cost optimization problem; the
technical foundation (S3 semantics) is table stakes.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ BLOB STORAGE ARCHITECTURE                           │
│                                                      │
│ UPLOAD (presigned URL):                            │
│  Client → POST /api/upload-request → App API      │
│  App API → S3 API: generate presigned PUT URL     │
│  App API → Client: {upload_url, object_key}       │
│  Client → S3: PUT {upload_url} [binary data]     │
│  Client → POST /api/upload-complete (key)        │
│  App API → S3 HEAD: verify object exists          │
│  App API → DB: store object_key in record         │
│                                                      │
│ READ (public, via CDN):                            │
│  Client → CDN → (hit) serve from edge            │
│               → (miss) fetch from S3, cache       │
│                                                      │
│ READ (private):                                     │
│  Client → GET /api/file/{id} → App API           │
│  App API: auth check, generate presigned GET URL  │
│  Client → presigned URL → S3 serves directly     │
│                                                      │
│ LIFECYCLE:                                          │
│  Day 0: upload → S3 Standard (hot)               │
│  Day 30: S3 lifecycle moves to IA (cool)         │
│  Day 90: moves to Glacier (cold/archive)         │
│  Day 2555 (7 years): deleted                     │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Presigned URL upload flow (Python/boto3)**
```python
import boto3
import uuid
import os
from typing import Optional

s3_client = boto3.client(
    's3',
    region_name='us-east-1',
    # Use IAM role in production, not access keys
)

BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
ALLOWED_CONTENT_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "application/pdf"
}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

def request_upload_url(
        user_id: int,
        content_type: str,
        file_extension: str) -> dict:
    """
    Step 1: Client requests a presigned upload URL.
    App validates, generates S3 presigned URL.
    Client uses the URL to upload directly to S3.
    App server never handles binary data.
    """
    # Validate content type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(
            f"Content type not allowed: {content_type}")
    
    # Generate unique, non-guessable object key
    object_key = (f"uploads/{user_id}/"
                  f"{uuid.uuid4()}.{file_extension}")
    
    # Generate presigned PUT URL with conditions
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': object_key,
            'ContentType': content_type,
        },
        ExpiresIn=300,  # URL valid for 5 minutes
    )
    
    return {
        "upload_url": presigned_url,
        "object_key": object_key,
        "expires_in": 300
    }

def confirm_upload(user_id: int,
                   object_key: str,
                   filename: str) -> str:
    """
    Step 2: Client confirms upload complete.
    App verifies object exists in S3.
    Stores reference in database.
    """
    # Verify object actually exists (not just trust client)
    try:
        head = s3_client.head_object(
            Bucket=BUCKET_NAME, Key=object_key)
        file_size = head['ContentLength']
        if file_size > MAX_FILE_SIZE_BYTES:
            # Delete oversized object
            s3_client.delete_object(
                Bucket=BUCKET_NAME, Key=object_key)
            raise ValueError("File exceeds size limit")
    except s3_client.exceptions.NoSuchKey:
        raise ValueError("Upload not found in S3")
    
    # Store in database (just the key, not full URL)
    db.execute(
        "UPDATE users SET avatar_key = %s "
        "WHERE id = %s",
        [object_key, user_id])
    
    return object_key

def generate_download_url(object_key: str,
                          expiry_seconds: int = 900
                          ) -> str:
    """
    Generate presigned GET URL for private objects.
    Expires in 15 minutes by default.
    Regenerate on each access (short TTL for security).
    """
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': object_key},
        ExpiresIn=expiry_seconds
    )

# BAD: streaming upload through app server
@app.post("/upload_bad")
async def upload_through_server(file: UploadFile):
    # BAD: file data goes through app server memory.
    # At 1000 concurrent 10MB uploads = 10GB RAM!
    contents = await file.read()  # 10MB in memory
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"uploads/{uuid.uuid4()}",
        Body=contents  # app server handles bytes
    )
```

**Example 2 - S3 lifecycle policy (Terraform)**
```hcl
resource "aws_s3_bucket_lifecycle_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  rule {
    id     = "transition-and-expire"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 2555  # 7 years (compliance)
    }

    # Clean up incomplete multipart uploads
    # after 7 days (important cost saving)
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  rule {
    id     = "delete-temp-uploads"
    status = "Enabled"

    filter {
      prefix = "tmp/"  # Temporary/unconfirmed uploads
    }

    expiration {
      days = 1  # Delete after 24h if not confirmed
    }
  }
}
```

---

### ⚖️ Comparison Table

| Approach | Scalability | Cost | Complexity | Use Case |
|---|---|---|---|---|
| **App server filesystem** | Poor (one server) | Low initially | Low | Dev only, not production |
| **NFS/shared filesystem** | Medium | Medium | Medium | Legacy systems, small scale |
| **Managed blob storage (S3)** | Infinite | Pay-per-use | Low-Medium | All production use cases |
| **Custom distributed storage** | Infinite | High CAPEX | Very high | Netflix/Dropbox/Uber scale |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Store the full S3 URL in the database | Store only the object key (`uploads/123/abc.jpg`), not the full URL (`https://bucket.s3.amazonaws.com/...`). URLs change: if you switch regions, rename buckets, add/remove CDN, or change URL structure, all stored URLs break. The key is the stable identifier. Construct the URL at read time from the key and your current configuration. |
| S3 object paths are real directories | S3 uses a flat key namespace. `images/user-123/photo.jpg` is just a string key with `/` as part of the name. There is no "images" directory. Listing objects with `prefix=images/` works by prefix matching on keys. This matters for performance: all keys with the same prefix land on the same S3 partition. Avoid sequential or time-based prefixes (e.g., all objects prefixed `2024-01-01-`) - they create hot partitions. Use random UUIDs or hash-based prefixes for uniform distribution. |
| Public S3 bucket for user uploads | Never make a bucket fully public. Use presigned URLs for private uploads, or CloudFront with Origin Access Control (OAC) for public reads. A public bucket allows anyone to list and download all objects, even if they don't know the URLs. Also: S3 "Block Public Access" settings exist at the account level - enable this as a safety net. |

---

### 🚨 Failure Modes & Diagnosis

**S3 Presigned URL Expiry Causing Upload Failures**

**Symptom:**
Users report: "File upload fails with a 403 error."
Uploads work in development but fail in production
for large files (> 1GB). Error message: "Request
has expired."

**Root Cause:**
Presigned URL TTL: 5 minutes. Large file upload time
over slow connection: 10+ minutes. URL expires during
upload. S3 rejects the PUT request with 403.

**Fix:**
```python
# Problem: too short TTL for large files
# Generate a longer TTL for large file uploads

def request_upload_url_v2(
        user_id: int,
        content_type: str,
        file_size_bytes: int,
        file_extension: str) -> dict:
    # Estimate upload time based on file size
    # Assume 5 Mbps upload speed (conservative)
    estimated_upload_seconds = (
        file_size_bytes / (5 * 1024 * 1024 / 8))
    
    # TTL = estimated time + 5 minute buffer
    ttl = max(300, int(estimated_upload_seconds + 300))
    ttl = min(ttl, 3600)  # Cap at 1 hour
    
    if file_size_bytes > 5 * 1024 * 1024:  # > 5MB
        # For large files: use multipart upload
        return initiate_multipart_upload(
            user_id, content_type, file_extension)
    
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': f"uploads/{user_id}/{uuid.uuid4()}",
            'ContentType': content_type,
        },
        ExpiresIn=ttl
    )
    return {"upload_url": presigned_url, "ttl": ttl}

def initiate_multipart_upload(
        user_id: int,
        content_type: str,
        file_extension: str) -> dict:
    """
    For large files: multipart upload.
    Each part gets its own presigned URL.
    Client uploads parts in parallel.
    Parts can be retried individually on failure.
    """
    object_key = (f"uploads/{user_id}/"
                  f"{uuid.uuid4()}.{file_extension}")
    
    response = s3_client.create_multipart_upload(
        Bucket=BUCKET_NAME,
        Key=object_key,
        ContentType=content_type
    )
    upload_id = response['UploadId']
    
    # Client will call /api/upload/part for each part
    return {
        "upload_type": "multipart",
        "upload_id": upload_id,
        "object_key": object_key
    }
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `URL Shortener Design` - introduces object store
  concepts; blob storage is the storage layer for
  binary objects (not metadata)

**Builds On This (learn these next):**
- `Video Streaming Design` - builds on blob storage
  (S3 for video segments) with CDN delivery layer
- `CDN Architecture Pattern` - CDN in front of blob
  store is standard architecture for public reads
- `File Storage System Design` - full file system
  (directory hierarchy, versioning, sharing, metadata)
  is built on top of blob storage

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Key-value store for binary data.          │
│             │ App server never handles binary bytes.   │
├─────────────┼──────────────────────────────────────────┤
  │
│ PRESIGNED   │ App generates URL. Client uploads direct │
│ UPLOAD      │ to S3. 50,000× less app bandwidth.       │
├─────────────┼──────────────────────────────────────────┤
  │
│ CDN         │ Put CloudFront in front of S3.           │
│             │ Public immutable files: TTL = 1 year.   │
├─────────────┼──────────────────────────────────────────┤
  │
│ DB STORAGE  │ Store object KEY, not full URL.         │
│             │ URL changes; key is stable.             │
├─────────────┼──────────────────────────────────────────┤
  │
│ MULTIPART   │ Files > 5MB: upload in chunks.          │
│             │ Parallel parts. Resumable.              │
├─────────────┼──────────────────────────────────────────┤
  │
│ LIFECYCLE   │ Standard → IA (30d) → Glacier (90d)    │
│             │ Abort incomplete multipart (7d).        │
├─────────────┼──────────────────────────────────────────┤
  │
│ SECURITY    │ Private bucket. Presigned URLs.         │
│             │ Block Public Access = enabled.          │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "S3 + presigned URLs + CDN.            │
│             │  Store key in DB, not URL."            │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ Payment System Design                    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use presigned URLs for uploads: client gets a
   time-limited URL from your API and uploads directly
   to S3. Your app server never handles binary data.
   This eliminates the bandwidth and memory bottleneck
   of proxying file uploads through your application.
2. Store the S3 object key in your database, not the
   full URL. The key is stable; URLs change with regions,
   bucket names, CDN domains. Construct the URL at read
   time from the key.
3. CDN in front of S3 for reads. Static files (images,
   videos) are immutable by design (new UUID = new key).
   Perfect CDN candidates (TTL: 1 year). S3 is not
   optimized for high-concurrency reads - CDN is.

**Interview one-liner:**
"Blob storage (S3): flat key-value store for binary objects. Upload: client
requests presigned PUT URL from app API → uploads directly to S3 (app server
never handles binary data). For large files: multipart upload (parallel parts,
resumable). Store object KEY in DB (not full URL - URL changes, key is stable).
Reads: CloudFront CDN in front of S3, TTL=1 year for immutable files (UUID in
key). Security: private bucket, presigned GET URLs for private files, Block
Public Access enabled. Lifecycle: S3 Standard → IA (30d) → Glacier (90d)."
