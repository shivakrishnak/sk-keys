---
id: SYD-049
title: Video Streaming Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-010
used_by: ""
related: SYD-008, SYD-010, SYD-014, SYD-031
tags:
  - architecture
  - video
  - streaming
  - cdn
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 49
permalink: /technical-mastery/syd/video-streaming-design/
---

⚡ TL;DR - Video streaming delivers video data
progressively (not as a full download) using adaptive
bitrate (ABR) streaming. A video is encoded into
multiple quality levels (240p to 4K) and segmented into
small chunks (2-10 seconds each). A manifest file (HLS
.m3u8 or DASH .mpd) describes all available qualities
and chunk URLs. The player downloads the manifest, then
continuously downloads the next chunk in the best
available quality for current network conditions. CDN
caches chunks globally. Origin stores only the master
copies. Key design: encode once, serve from CDN everywhere.

| #049 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, CDN | |
| **Related:** | Caching, CDN Architecture Pattern, Load Balancer, Sharding | |

---

### 🔥 The Problem This Solves

Netflix has 270M subscribers streaming simultaneously
at peak. A movie is 4GB at 1080p. If each of 10M
concurrent viewers downloaded the full file from one
server: 10M × 4GB = 40PB of bandwidth at once. No
single server or data center can handle this. The
file must be distributed globally, delivered
progressively (not all at once), and adapted to each
user's network speed to prevent buffering.

---

### 📘 Textbook Definition

**Video streaming:** Continuous delivery of video data
over a network, allowing playback to begin before the
full video is downloaded. The server delivers segments
of video progressively; the client buffers a few seconds
ahead of playback.

**Adaptive Bitrate Streaming (ABR):** A technique where
video is encoded at multiple quality levels. The player
dynamically switches between quality levels based on
current bandwidth. If network speed drops, the player
switches to a lower quality to avoid buffering.

**HLS (HTTP Live Streaming):** Apple's ABR protocol.
Segments video into .ts files (2-10 seconds each).
Manifest file (.m3u8) lists all segment URLs and
available quality levels. Widely supported.

**MPEG-DASH:** ISO standard for ABR streaming.
Segments into .mp4 fragments. More flexible than HLS.
Used by YouTube and Netflix.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Video → encode at multiple qualities → chunk into
segments → serve manifest + chunks via CDN →
player downloads segments adaptively.

**One analogy:**
> Streaming a YouTube video is like reading a very
> long book that is delivered one page at a time by mail:
>
> - The publisher (encoder) printed the book at different
>   font sizes (quality levels): large print for slow
>   readers (low bandwidth), normal print for most, and
>   microscopic text for speed-readers with a magnifier
>   (4K for fast connections).
>
> - Instead of mailing the whole book at once, pages arrive
>   continuously, slightly ahead of your reading pace.
>
> - If the mail gets slow (bandwidth drops), you automatically
>   switch to the large-print version of the remaining pages
>   (lower quality) so you never have to stop reading.

**One insight:**
The CDN is the foundation. Video chunks are static files
(they never change once encoded). Static files cached
at CDN edge nodes near the user eliminate the origin
server as the bottleneck. At Netflix: ~95% of traffic
served by CDN, with < 5% cache misses reaching the origin.

---

### 🔩 First Principles Explanation

**VIDEO ENCODING PIPELINE:**
```
Upload ──► Raw Video Storage (S3/Blob)
        └──► Transcoding Workers (FFmpeg cluster)
              ├── 240p  (200 Kbps)
              ├── 360p  (500 Kbps)
              ├── 480p  (1 Mbps)
              ├── 720p  (2.5 Mbps)
              ├── 1080p (5 Mbps)
              └── 4K    (15-25 Mbps)
              Each quality → segmented into 4-second chunks

Segment naming:
  video_1080p_001.ts (segment 1, 1080p, 4 seconds)
  video_1080p_002.ts (segment 2, 1080p, 4 seconds)
  video_720p_001.ts  (segment 1, 720p, 4 seconds)
  ...

Manifest file (HLS .m3u8):
  #EXTM3U
  #EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
  video_1080p.m3u8
  #EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
  video_720p.m3u8
  #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480
  video_480p.m3u8

Per-quality manifest (video_1080p.m3u8):
  #EXTM3U
  #EXT-X-TARGETDURATION:4
  #EXTINF:4.0,
  https://cdn.example.com/video123/1080p/seg001.ts
  #EXTINF:4.0,
  https://cdn.example.com/video123/1080p/seg002.ts
  ...
```

**ADAPTIVE BITRATE ALGORITHM:**
```
Player maintains bandwidth estimate (EWMA of
recent segment download speeds).

Download loop:
  while not done:
    bandwidth = estimate_current_bandwidth()
    next_quality = select_quality(bandwidth, buffer_level)
    segment = download_next_segment(next_quality)
    buffer.append(segment)

Quality selection heuristics:
  buffer_level > 20 sec: upgrade quality if bandwidth
    allows
  buffer_level < 5 sec: downgrade quality immediately
  buffer_level < 1 sec: enter stall (buffering spinner)
  
  Target: stay above 10 seconds buffer.
  Switch quality only when bandwidth changes by >20%
    (prevent thrashing - rapidly switching quality).
```

**CDN CACHING STRATEGY:**
```
Video segments: long TTL (1 year)
  Content is immutable (once encoded, never changes).
  Cache-Control: public, max-age=31536000, immutable

Manifest file: short TTL (5-30 seconds for live streams)
  For on-demand: longer TTL (1 hour) since segment list
  doesn't change after processing is complete.
  
  Cache-Control: public, max-age=3600

CDN cache key: full URL path
  /video/123/1080p/seg001.ts → cached per segment
  Per region: segment cached at each PoP (Point of
    Presence)

First viewer per region: CDN miss → fetch from origin →
  cache
  All subsequent viewers: CDN hit → served from edge
  Popular videos: 100% CDN hit rate after first viewer
```

---

### 🧪 Thought Experiment

**SIZING: Netflix-scale video streaming**

Subscribers: 270M. Peak concurrent streams: 15M.
Average bitrate: 4 Mbps (mix of mobile+TV).
Total peak bandwidth: 15M × 4 Mbps = 60 Tbps.

Netflix's CDN (Open Connect Appliances) provides
more than 200 Tbps. This capacity is headroom for
new video releases, live events, and redundancy.

**Storage sizing:**
Average movie duration: 2 hours = 7,200 seconds.
At 5 Mbps (1080p): 7,200 × 5Mbps / 8 = 4.5GB per movie per quality.
Netflix library: ~20,000 titles × 6 quality levels:
  20,000 × 6 × 4.5GB = 540TB of encoded video.
Plus 4K (25 Mbps): add another 100TB.
Total: ~1-2 PB for the full encoded library.
(Small! The real cost is bandwidth, not storage.)

**Transcoding cost:**
A 2-hour movie at 6 quality levels: ~12 hours of CPU time per title.
30,000 new titles/year: 30,000 × 12 hours = 360,000 CPU-hours/year.
~41 CPU-years, spread across thousands of cloud VMs.
Transcoding is bursty: parallelize per segment across many VMs.

---

### 🧠 Mental Model / Analogy

> Video streaming is like a highway with multiple lanes:
>
> - The video is the journey from A to B.
> - Each quality level is a different lane (1, 2, 3, 4, 5).
> - Traffic conditions (bandwidth) determine which lane
>   you can safely drive in.
> - When traffic is clear: drive in the fast lane (4K).
> - When congestion appears: merge to a slower lane
>   (720p) rather than stopping entirely.
> - The segment buffer = the cars already on the road
>   ahead of you. If you have 20 cars (seconds) buffered,
>   you can afford to switch lanes without stopping.
>
> CDN = local highway interchanges: you don't drive
> back to the city (origin) for every mile. The
> highway exists near you already.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Video streaming sends video a few seconds at a time.
Your phone or computer downloads the next few seconds
while you watch the current seconds. If your internet
is slow, it automatically switches to a lower quality
so the video doesn't pause.

**Level 2 - How to use it (junior developer):**
Videos are pre-encoded into multiple quality levels
using FFmpeg. Each level is split into short segments
(4 seconds). A manifest file lists all segments.
The player reads the manifest, downloads segments,
and tracks network speed to pick the best quality.
CDN serves the static segment files globally.

**Level 3 - How it works (mid-level engineer):**
Upload → async transcoding pipeline (FFmpeg workers
triggered by S3 event) → encode 6+ quality levels →
segment into 4-second chunks → store chunks in S3 +
CDN distribution. Player downloads master manifest
(quality level list), then quality-specific manifest
(segment URLs), then adaptive download of segments.
CDN caches segments at edge nodes with 1-year TTL
(immutable content). ABR algorithm selects quality
based on bandwidth estimate and buffer level.

**Level 4 - Why it was designed this way (senior/staff):**
The 4-second segment size is a balance between:
- Startup latency (longer segments = more data to download
  before first play)
- Switch granularity (shorter segments = faster quality
  adaptation, but more HTTP requests overhead)
- CDN efficiency (very short segments = very many cache entries)
4 seconds is the most common production default.
The manifest URL is the entry point that CDN can cache or
invalidate (for live streams, short TTL). Segments use
immutable URLs (content-addressed: segment content never
changes after encoding). This allows indefinite CDN caching.
Transcoding is async because it takes 10-30× real-time
duration; a 2-hour movie takes ~2 hours to transcode
at full quality (CPU-intensive). Use distributed FFmpeg
workers (e.g., AWS MediaConvert or Zencoder) for parallelism.

**Level 5 - Mastery (distinguished engineer):**
Netflix runs its own CDN (Open Connect). At 200+ Tbps,
commercial CDNs are too expensive and too inflexible.
Netflix pre-positions videos (proactively pushes popular
titles to edge servers before they are requested) using
ML prediction of viewing patterns. Key algorithm: which
videos will be watched most in the next 24 hours in each
city? Pre-position those during off-peak hours to avoid
cold-cache misses during peak viewing. Second challenge:
per-title quality optimization. Netflix uses per-scene
encoding (Content-Aware Encoding): static talking scenes
compress well at lower bitrate; action scenes need higher
bitrate for the same perceptual quality. By encoding
variably (not at a fixed bitrate), Netflix reduces average
file size by 20-50% without reducing visual quality.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ VIDEO STREAMING DATA FLOW                           │
│                                                      │
│ UPLOAD:                                             │
│  Creator ──► Upload API ──► S3 (raw video)         │
│  S3 event ──► Transcoding Queue (SQS)              │
│  FFmpeg Workers: encode 6 qualities, segment 4s    │
│  Output: 6 × N segments per video → S3             │
│  Master manifest + quality manifests → S3          │
│  CDN distribution triggered                        │
│                                                      │
│ PLAYBACK:                                           │
│  1. Client: GET /video/123/master.m3u8 → CDN       │
│     Returns: list of quality manifests             │
│  2. Player: GET /video/123/1080p.m3u8 → CDN       │
│     Returns: list of segment URLs (1080p)          │
│  3. Player downloads seg001.ts → CDN edge (< 50ms) │
│  4. Measures bandwidth, selects next quality        │
│  5. Download seg002.ts (quality may change)        │
│  6. Continues until video ends                     │
│                                                      │
│ CDN CACHE MISS:                                     │
│  CDN ──► origin S3 ──► CDN stores for 1 year      │
│  Subsequent requests: served from CDN edge         │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Transcoding pipeline trigger (Python)**
```python
import boto3
import json
import subprocess
import os

s3 = boto3.client("s3")
sqs = boto3.client("sqs")

QUALITIES = [
    {"name": "240p",  "width": 426,  "height": 240,
     "bitrate": "200k",  "audio": "64k"},
    {"name": "480p",  "width": 854,  "height": 480,
     "bitrate": "1000k", "audio": "128k"},
    {"name": "720p",  "width": 1280, "height": 720,
     "bitrate": "2500k", "audio": "192k"},
    {"name": "1080p", "width": 1920, "height": 1080,
     "bitrate": "5000k", "audio": "192k"},
]

def transcode_video(video_id: str,
                     input_path: str,
                     output_bucket: str):
    """
    Transcode video to multiple quality levels.
    Produces HLS segments (.ts) and manifests (.m3u8).
    """
    output_dir = f"/tmp/{video_id}"
    os.makedirs(output_dir, exist_ok=True)

    quality_manifests = []
    for q in QUALITIES:
        quality_dir = f"{output_dir}/{q['name']}"
        os.makedirs(quality_dir, exist_ok=True)

        # FFmpeg: transcode + segment into 4s HLS chunks
        cmd = [
            "ffmpeg", "-i", input_path,
            "-vf", f"scale={q['width']}:{q['height']}",
            "-c:v", "libx264", "-b:v", q["bitrate"],
            "-c:a", "aac", "-b:a", q["audio"],
            "-hls_time", "4",         # 4-second segments
            "-hls_playlist_type", "vod",
            "-hls_segment_filename",
            f"{quality_dir}/seg%03d.ts",
            f"{quality_dir}/playlist.m3u8"
        ]
        subprocess.run(cmd, check=True)

        # Upload segments to S3
        for fname in os.listdir(quality_dir):
            s3.upload_file(
                f"{quality_dir}/{fname}",
                output_bucket,
                f"videos/{video_id}/{q['name']}/{fname}",
                ExtraArgs={
                    "ContentType": "application/x-mpegURL"
                    if fname.endswith(".m3u8")
                    else "video/MP2T",
                    # Immutable segments: cache 1 year
                    "CacheControl": "public, max-age=31536000"
                    if fname.endswith(".ts")
                    else "public, max-age=3600",
                }
            )
        quality_manifests.append(
            (q["name"], q["bitrate"], q["width"], q["height"])
        )

    # Generate master manifest
    master = "#EXTM3U\n"
    bw_map = {"240p": 200000, "480p": 1000000,
               "720p": 2500000, "1080p": 5000000}
    for name, _, w, h in quality_manifests:
        master += (
            f"#EXT-X-STREAM-INF:"
            f"BANDWIDTH={bw_map[name]},"
            f"RESOLUTION={w}x{h}\n"
            f"https://cdn.example.com/videos/"
            f"{video_id}/{name}/playlist.m3u8\n"
        )
    s3.put_object(
        Bucket=output_bucket,
        Key=f"videos/{video_id}/master.m3u8",
        Body=master.encode(),
        ContentType="application/x-mpegURL",
        CacheControl="public, max-age=3600"
    )
    print(f"Transcoding complete for {video_id}")
```

**Example 2 - Serving full video before transcoding (BAD)**
```python
# BAD: Serve raw uploaded video directly to users
# while encoding runs in the background

@app.get("/video/{video_id}/stream")
def stream_video_bad(video_id: str):
    # Streams raw 4GB .mov file directly from server
    # No segmentation: user downloads the whole file
    # No quality adaptation: stuck at one quality
    # All traffic hits origin server: no CDN
    # 10K concurrent viewers: 40TB from one server
    raw_path = get_raw_video_path(video_id)
    return FileResponse(raw_path)

# GOOD:
# 1. Wait for transcoding to complete before marking
#    video as "available" to viewers.
# 2. Return the manifest URL (CDN-backed), not the
#    raw file.
# 3. Player handles adaptive streaming from CDN.

@app.get("/video/{video_id}/manifest")
def get_manifest(video_id: str):
    video = db.get_video(video_id)
    if video.status != "ready":
        return {"error": "Video processing"}
    # Return CDN URL for master manifest
    cdn_url = f"https://cdn.example.com/videos/{video_id}/master.m3u8"
    return {"manifest_url": cdn_url}
```

---

### ⚖️ Comparison Table

| Protocol | Segment Format | Latency | Browser Support | Use Case |
|---|---|---|---|---|
| **HLS** | .ts / .fmp4 | 6-30s (on-demand) | Universal | VOD, live (Apple/iOS required) |
| **MPEG-DASH** | .mp4 fragments | 2-30s | Most browsers | VOD, Netflix/YouTube |
| **WebRTC** | RTP packets | < 1 second | All modern | Real-time (video calls) |
| **RTMP** | FLV | 1-5s | Requires Flash (deprecated) | Legacy live streaming |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Video streaming requires special streaming protocols | Modern video streaming uses plain HTTP for delivery. HLS and DASH segments are served as regular HTTP requests. CDNs cache them like any other static content. The "streaming" is in the client downloading segments progressively, not in any server-side streaming protocol. |
| Higher bitrate always means better quality for the viewer | If the viewer's bandwidth is 2 Mbps and you send a 5 Mbps segment, it takes 2.5x real-time to download. The buffer drains. The player must stall (buffering spinner). A 1.5 Mbps (720p) stream that downloads smoothly looks better than a stalled 1080p stream. ABR's job is to choose the highest quality that fits within current bandwidth. |
| All videos should be encoded the same way | Content-Aware Encoding (Netflix's Per-Title Encode Optimization) encodes each video differently. An animated film with flat colors needs much lower bitrate for the same quality as a live-action film with high-motion scenes. One-size-fits-all encoding wastes bandwidth for easy-to-compress content and degrades quality for hard-to-compress content. |

---

### 🚨 Failure Modes & Diagnosis

**Buffering at Start of Playback**

**Symptom:**
Users experience a 5-10 second loading spinner before
video begins. Once started, playback is smooth.
Affects all users, not just slow connections.

**Root Cause:**
The master manifest is not cached at CDN (or has
expired). Every play request triggers a CDN miss
→ request goes to origin. Origin is under heavy load
due to a popular video launch. Origin responds in
3-5 seconds. This is the "startup latency."

**Diagnosis:**
```bash
# Check CDN cache hit rate for the manifest
curl -I "https://cdn.example.com/video/123/master.m3u8"
# Look for: X-Cache: HIT vs MISS
# If X-Cache: MISS on repeat requests: manifest not caching

# Check Cache-Control header returned by origin
# Should be: Cache-Control: public, max-age=3600
# If private or no-cache: CDN won't cache it

# Check origin response time
curl -w "@curl-format.txt" -o /dev/null -s \
  "https://origin.example.com/video/123/master.m3u8"
```

**Fix:**
```python
# Ensure manifest has correct cache headers
s3.put_object(
    Bucket=bucket,
    Key=f"videos/{video_id}/master.m3u8",
    Body=manifest_content.encode(),
    ContentType="application/x-mpegURL",
    # Explicitly allow CDN caching of manifest
    CacheControl="public, max-age=3600, s-maxage=3600",
)

# For popular video launches: pre-warm CDN
# Push manifest to CDN nodes before public release
# (CDN providers offer cache pre-warming APIs)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching` - CDN caching of segments is the entire
  scaling strategy for video delivery
- `CDN Architecture Pattern` - CDN edge nodes serve
  95%+ of video traffic

**Builds On This (learn these next):**
- `Load Balancer` - origin servers behind load balancer
  for the 5% cache misses
- `Sharding` - user video metadata sharded by user_id

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ENCODE      │ 6+ quality levels (240p to 4K).           │
│             │ FFmpeg → 4-second HLS/DASH segments       │
├─────────────┼──────────────────────────────────────────┤
  │
│ MANIFEST    │ Master (quality list) + per-quality       │
│             │ (segment URLs). Player reads, selects ABR │
├─────────────┼──────────────────────────────────────────┤
  │
│ CDN         │ Segments: 1-year immutable TTL.           │
│             │ Manifests: 1-hour TTL (or 30s for live)  │
├─────────────┼──────────────────────────────────────────┤
  │
│ ABR         │ Switch quality when bandwidth changes     │
│             │ > 20%. Target > 10s buffer. Protect       │
│             │ against quality thrashing.               │
├─────────────┼──────────────────────────────────────────┤
  │
│ PIPELINE    │ Upload → S3 → SQS → FFmpeg workers       │
│             │ → S3 segments + manifests → CDN           │
├─────────────┼──────────────────────────────────────────┤
  │
│ FAILURE     │ Startup stall: manifest not CDN cached.  │
│             │ Fix: correct Cache-Control headers.      │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Encode → segment → CDN. ABR lets       │
│             │  player adapt quality to bandwidth."    │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ Ride-Sharing System Design               │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Adaptive Bitrate (ABR): video encoded at 6+ quality
   levels, segmented into 4-second chunks. Player
   downloads segments progressively, switching quality
   based on current bandwidth to avoid buffering.
2. CDN is the entire scaling strategy. Segments are
   immutable static files - cache them at CDN edges
   with a 1-year TTL. 95%+ of traffic served from CDN.
   Origin only sees the rare cache miss.
3. Upload triggers async transcoding (S3 event → SQS
   → FFmpeg workers). Video is not available for
   playback until transcoding completes. Serve only
   the CDN manifest URL to players - never serve raw
   video files directly from your origin server.

**Interview one-liner:**
"Video streaming: upload to S3 → async transcoding pipeline (FFmpeg workers,
triggered by SQS) encodes 6 quality levels (240p-4K) and segments each into
4-second HLS/DASH chunks. Store segments in S3 with 1-year immutable CDN cache.
Players download master manifest → quality manifest → segments adaptively (ABR:
select quality matching current bandwidth, target > 10s buffer, avoid quality
thrashing). CDN serves 95%+ of traffic; origin only sees cold misses. Failure:
startup latency when manifest is not CDN-cached - ensure Cache-Control header
allows CDN caching."
