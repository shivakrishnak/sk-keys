---
layout: default
title: "Video Streaming Design"
parent: "System Design"
nav_order: 724
permalink: /system-design/video-streaming-design/
number: "724"
category: System Design
difficulty: ★★★
depends_on: "CDN, Object Storage, Caching"
used_by: "System Design Interview"
tags: #advanced, #system-design, #interview, #streaming, #cdn
---

# 724 — Video Streaming Design

`#advanced` `#system-design` `#interview` `#streaming` `#cdn`

⚡ TL;DR — **Video Streaming Design** converts uploaded videos into adaptive bitrate segments (HLS/DASH), distributes them via CDN edge nodes, and dynamically adjusts quality to available bandwidth — enabling billions of streams with no single server bottleneck.

| #724            | Category: System Design      | Difficulty: ★★★ |
| :-------------- | :--------------------------- | :-------------- |
| **Depends on:** | CDN, Object Storage, Caching |                 |
| **Used by:**    | System Design Interview      |                 |

---

### 📘 Textbook Definition

A **Video Streaming System** enables users to watch video content over the internet without downloading the entire file first. The two key components are: (1) **Transcoding pipeline**: uploaded raw video is converted into multiple resolution/bitrate variants (e.g., 240p/400kbps, 480p/1Mbps, 1080p/4Mbps, 4K/15Mbps) using distributed transcoding workers, then segmented into short chunks (2-6 seconds each) for adaptive streaming; (2) **Delivery infrastructure**: video segments are stored in object storage (S3) and distributed via CDN edge nodes globally, so viewers receive video from a nearby edge server rather than the origin. **Adaptive Bitrate Streaming (ABR)** protocols (HLS — HTTP Live Streaming, MPEG-DASH) allow the player to dynamically switch between quality levels based on the viewer's current network bandwidth. This architecture enables Netflix, YouTube, and TikTok to serve billions of concurrent streams with sub-second latency adaptation and no single bottleneck.

---

### 🟢 Simple Definition (Easy)

Video Streaming: Netflix stores your movie in 6 different quality versions (360p, 480p, 720p, 1080p, etc.), each cut into 4-second segments. Netflix's video player checks your internet speed every 4 seconds and downloads the appropriate quality segment. Good internet → 1080p. Bad internet → drops to 480p seamlessly. Segments are cached at Netflix's servers near you (CDN) — not downloaded from Netflix's main server in the USA.

---

### 🔵 Simple Definition (Elaborated)

YouTube architecture: User uploads a 4K video → Upload Service stores raw file in Google Cloud Storage → Transcoding Workers convert it into 8 quality variants (360p to 4K) + 4-second segments → Segments uploaded to Google's CDN. When viewer plays: player downloads a manifest file (M3U8 or MPD) listing all available quality levels → player downloads first 4-second segment at highest quality it can handle → if bandwidth drops, next segment fetched at lower quality → seamless degradation without buffering. The entire video is never on the player's device — only the current and next few segments are buffered.

---

### 🔩 First Principles Explanation

**Video transcoding pipeline and adaptive bitrate streaming:**

```
VIDEO UPLOAD PIPELINE:

  1. Client: uploads raw video file (MOV, MKV, MP4) to Upload Service
     Direct upload: pre-signed S3 URL (client uploads directly to S3, bypassing servers)

     // Server generates pre-signed URL:
     String uploadUrl = s3.generatePresignedUrl("my-bucket", "raw/" + videoId,
                                                  PUT, expiry=15min)
     // Client: HTTP PUT raw_video.mp4 → uploadUrl (goes directly to S3, not through server)
     // Server is not in the upload data path → no bandwidth bottleneck

  2. S3 Event Notification → triggers Transcoding Job:
     raw/video-456.mp4 uploaded → SNS → SQS → Transcoding Workers

  3. TRANSCODING WORKERS (distributed, parallelised):

     Input: raw/video-456.mp4

     Step 1: Validation
       - Check format, duration, file size
       - Scan for malware/CSAM (hash-based + ML classifier)

     Step 2: Split into segments
       ffmpeg -i raw.mp4 -segment_time 4 -f segment raw_seg_%04d.mp4
       → raw_seg_0000.mp4 (0-4s), raw_seg_0001.mp4 (4-8s), ...

     Step 3: Parallel transcoding of each resolution:
       Worker A: transcode all segments → 1080p/4Mbps (H.264 or H.265)
       Worker B: transcode all segments → 720p/2.5Mbps
       Worker C: transcode all segments → 480p/1Mbps
       Worker D: transcode all segments → 360p/400Kbps

       Parallelism: 4K video (2 hours) = 1800 segments × 4 resolutions = 7200 tasks.
       With 100 workers: 72 tasks per worker → complete in parallel.

     Step 4: Generate HLS manifest (M3U8):
       #EXTM3U
       #EXT-X-VERSION:3

       #EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=1920x1080
       1080p/index.m3u8

       #EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
       720p/index.m3u8

       #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480
       480p/index.m3u8

     Step 5: Upload all segments + manifests to S3:
       s3://video-segments/video-456/1080p/seg_0001.ts
       s3://video-segments/video-456/1080p/seg_0002.ts
       ...
       s3://video-segments/video-456/master.m3u8

     Step 6: Update video metadata DB:
       videos.status = READY
       videos.duration = 7234 seconds
       videos.available_qualities = [1080p, 720p, 480p, 360p]

ADAPTIVE BITRATE STREAMING (ABR) PLAYER:

  Player startup:
  1. Fetch master.m3u8 (manifest listing all quality levels + bandwidth)
  2. Estimate bandwidth: time first segment download → bytes/seconds
  3. Select quality: choose highest quality below 80% of estimated bandwidth
     (80% safety margin = don't select quality equal to full bandwidth — causes rebuffering)

  Ongoing adaptation:
    Measure download speed of each segment.
    If speed > current_quality_bandwidth × 1.5: upgrade to next quality level.
    If speed < current_quality_bandwidth × 0.7: downgrade to lower quality.

    Buffer-based adaptation (more sophisticated):
      Buffer > 30 seconds: upgrade quality.
      Buffer < 10 seconds: downgrade quality.
      Buffer < 3 seconds: CRITICAL — stall imminent → immediately go to lowest quality.

    Algorithm: Netflix's BOLA, Apple's ABR algorithm, etc.

CDN DELIVERY:

  Video segment request flow:

  Player: GET https://cdn.example.com/video-456/1080p/seg_0042.ts

  1. DNS resolves cdn.example.com → nearest CDN PoP (Point of Presence)
     (Anycast or DNS-based geolocation)

  2. CDN Edge (e.g., Frankfurt):
     Cache hit: serve seg_0042.ts from edge cache (< 10ms)
     Cache miss: fetch from S3 origin, cache locally, serve to player

  3. CDN caching for video segments:
     Long TTL (segments never change): Cache-Control: max-age=31536000 (1 year)
     Short TTL for manifests (M3U8): Cache-Control: max-age=2 (live streaming)

  CDN popularity effect:
     Popular video (1M concurrent viewers): first viewer = cache miss (fetch from S3).
     All subsequent viewers: CDN cache hit. S3 serves 1 request, not 1M.
     S3 request cost: essentially zero for popular content.

  CACHE HIT RATIO OPTIMIZATION:
     Segment naming: deterministic (video-456/1080p/seg_0042.ts) → all users share cache.
     Session tokens: NOT in segment URL (would make each user's URL unique → no cache sharing).
     Authentication: done at manifest level or via signed CDN URLs (short-lived token in URL).

LIVE STREAMING (different from VOD):

  VOD (Video on Demand): all segments pre-transcoded. CDN TTL = 1 year.
  Live: segments generated in real-time. CDN TTL = 2 seconds.

  Live streaming latency:
    Encoder (OBS): captures video → encodes to H.264 → pushes RTMP/SRT to ingest server
    Ingest server: receives RTMP → segments into 2-second HLS chunks → uploads to S3
    CDN: fetches latest 2-second segment every 2 seconds → serves to viewers

    Total latency: encode (1s) + upload (1s) + CDN propagation (1s) + player buffer (6s) = ~10s
    Ultra-low latency (LL-HLS, WebRTC): 2-5 seconds. Used for live sports, auctions.

STORAGE ESTIMATION:

  YouTube scale:
    500 hours of video uploaded per minute.
    Average video: 10 minutes × 4 quality levels × 4 segments/minute = 160 segments.
    Segment size (1080p, 4 seconds): ~2 MB.
    Storage per video: 160 segments × 4 qualities × 2 MB avg = ~1.3 GB per 10-minute video.
    Per minute of uploads: 500 videos × 1.3 GB = 650 GB/minute = ~11 TB/hour.
    Per year: 11 TB/hour × 8760 hours = ~96 petabytes/year.

    S3 cost: 96 PB × $0.023/GB = ~$2.2M/month (storage only).
    CDN: saves massive bandwidth costs (S3 egress: $0.09/GB; CDN is cheaper at scale).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT video streaming architecture:

- Single raw video file served from origin: one popular video = one server overwhelmed
- Fixed quality: good connection wastes bandwidth; bad connection = constant buffering
- No CDN: viewers far from origin server = high latency = buffering

WITH video streaming architecture:
→ CDN: popular video segments cached at 200+ edge nodes globally → consistent < 20ms delivery
→ ABR: dynamic quality switching → continuous playback regardless of network fluctuations
→ Segmentation: seek to any position instantly (jump to segment N without downloading 1-N)

---

### 🧠 Mental Model / Analogy

> A water supply system with pressure-adaptive valves. Water (video data) flows from a reservoir (S3 origin) through regional distribution centres (CDN PoPs) into homes via adaptive pressure valves (ABR player). If your home's pipe has high pressure (fast internet): valve opens fully (4K stream). If pressure drops (slow connection): valve automatically reduces flow to match capacity (720p) — you never run out of water (buffering). The regional distribution centre stores frequently needed water locally (CDN cache) — you don't always pull from the main reservoir.

"Reservoir" = S3 origin (stores all video segments)
"Regional distribution centres" = CDN PoPs (cached copies near viewers)
"Pressure-adaptive valve" = ABR player (switches quality based on bandwidth)
"Valve opens fully" = high-quality stream (fast internet)
"Automatic pressure reduction" = quality downgrade (bandwidth drop)
"Pull from local centre, not reservoir" = CDN cache hit (no S3 fetch)

---

### ⚙️ How It Works (Mechanism)

**HLS adaptive streaming: manifest and segment structure:**

```
Master playlist (master.m3u8):
  #EXTM3U
  #EXT-X-VERSION:3

  # 4K (15 Mbps):
  #EXT-X-STREAM-INF:BANDWIDTH=15000000,RESOLUTION=3840x2160,CODECS="avc1.640033,mp4a.40.2"
  4k/video.m3u8

  # 1080p (4 Mbps):
  #EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=1920x1080,CODECS="avc1.64001F,mp4a.40.2"
  1080p/video.m3u8

  # 720p (2.5 Mbps):
  #EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
  720p/video.m3u8

  # 480p (1 Mbps):
  #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480
  480p/video.m3u8

Resolution playlist (1080p/video.m3u8):
  #EXTM3U
  #EXT-X-VERSION:3
  #EXT-X-TARGETDURATION:4   ← each segment is ~4 seconds
  #EXT-X-MEDIA-SEQUENCE:0

  #EXTINF:4.004,
  seg_0001.ts              ← video segment 1 (0-4 seconds)
  #EXTINF:4.004,
  seg_0002.ts              ← video segment 2 (4-8 seconds)
  #EXTINF:3.985,
  seg_0003.ts
  ...
  #EXT-X-ENDLIST           ← marks VOD (not live streaming)
```

**Transcoding job queue (Spring Boot + AWS Batch):**

```java
@Service
public class TranscodingOrchestrator {

    @Autowired private AWSBatch awsBatch;
    @Autowired private VideoRepository videoRepository;

    // Triggered by S3 event notification on raw video upload:
    public void startTranscoding(String rawVideoKey, String videoId) {
        // Update status:
        videoRepository.updateStatus(videoId, VideoStatus.TRANSCODING);

        // Launch parallel transcoding jobs for each resolution:
        String[] qualities = {"4k", "1080p", "720p", "480p", "360p"};

        for (String quality : qualities) {
            SubmitJobRequest jobRequest = SubmitJobRequest.builder()
                .jobName("transcode-" + videoId + "-" + quality)
                .jobQueue("video-transcoding-queue")
                .jobDefinition("ffmpeg-transcoder")
                .containerOverrides(ContainerOverrides.builder()
                    .command(List.of(
                        "transcode.sh",
                        "--input", "s3://raw-videos/" + rawVideoKey,
                        "--output", "s3://video-segments/" + videoId + "/" + quality + "/",
                        "--quality", quality,
                        "--segment-duration", "4"
                    ))
                    .build())
                .build();

            awsBatch.submitJob(jobRequest);
        }

        // Separate job: generate master manifest after all qualities complete:
        // (use AWS Step Functions state machine to wait for all quality jobs → generate manifest)
    }

    // Called by each transcoding job on completion:
    public void onTranscodingComplete(String videoId, String quality, int segmentCount) {
        videoRepository.markQualityReady(videoId, quality, segmentCount);

        if (videoRepository.allQualitiesReady(videoId)) {
            generateMasterManifest(videoId);
            videoRepository.updateStatus(videoId, VideoStatus.READY);
            // Notify upload service → video is now playable
        }
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Raw video upload (single file, one resolution)
        │
        ▼
Video Streaming Design ◄──── (you are here)
(transcode → segment → CDN → ABR)
        │
        ├── CDN (deliver segments from edge, not origin)
        ├── Object Storage (S3 — durable segment storage)
        └── ABR (player-side quality adaptation algorithm)
```

---

### 💻 Code Example

**Signed CDN URL generation for authenticated video access:**

```java
// Generate time-limited CloudFront signed URL for video access:
// Prevents unauthorized sharing of premium content

@Service
public class VideoAccessService {

    @Autowired private CloudFrontSigner cloudFrontSigner;

    public String getPlaybackUrl(String videoId, long userId) {
        // Verify user has access (subscription, purchased, etc.):
        if (!hasAccess(userId, videoId)) {
            throw new AccessDeniedException("No subscription or purchase for video: " + videoId);
        }

        // Generate signed URL pattern (covers all segments for this video):
        String resourcePattern = "https://cdn.example.com/videos/" + videoId + "/*";
        Instant expiry = Instant.now().plus(6, ChronoUnit.HOURS);  // 6h viewing window

        // CloudFront cookie-based auth (better than per-segment signed URLs):
        SignedCookies cookies = cloudFrontSigner.createSignedCookies(
            resourcePattern, expiry, privateKey
        );

        // Client: store these cookies → all subsequent segment requests automatically authenticated
        // CDN validates cookie on every segment request → revocable (expire cookie = revoke access)

        return "https://cdn.example.com/videos/" + videoId + "/master.m3u8";
        // Note: cookies sent separately in response headers, not in URL
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Higher resolution always means better quality         | Perceived quality depends on resolution, bitrate, codec efficiency, and display size. A 1080p video at 1Mbps (heavily compressed) looks worse than 720p at 2.5Mbps. H.265/HEVC provides similar quality to H.264 at half the bitrate, reducing CDN and storage costs. Netflix encodes at varying bitrates per title based on content complexity (still animation = low bitrate; action movie = high bitrate)      |
| CDN caching means all videos are always fast          | CDN cache hit rate depends on content popularity. A rarely watched video (1 view/day): each view = CDN cache miss → origin fetch → high latency for viewer. Popular content (1M views/day): CDN cache hit ratio near 100%. For long-tail content (niche videos), CDN adds latency rather than reducing it. Some providers use tiered CDN (edge + regional cache + origin) to improve hit rates for long-tail      |
| Video streaming is just serving large files over HTTP | HTTP range requests allow downloading arbitrary byte ranges, but they don't provide quality adaptation, seek optimization, or DRM integration. HLS/DASH are specifically designed for streaming: short segments allow quality switching at every boundary; manifest files enable seek without scanning the entire file; DRM integration (AES-128 encryption, Widevine, PlayReady) is standardised                 |
| Transcoding is a one-time operation per video         | Many platforms re-transcode existing videos when: (1) new codec becomes available (H.264 → H.265 reduces storage 50%); (2) new resolution formats added (SD → HD → 4K → 8K); (3) content is flagged for quality issues. YouTube has re-transcoded its entire library multiple times. This requires efficient job scheduling, prioritization (newly uploaded > old content), and incremental re-encoding pipelines |

---

### 🔥 Pitfalls in Production

**Transcoding bottleneck on viral upload:**

```
PROBLEM: Video goes viral during transcoding → millions try to watch before transcoding finishes

  Creator uploads 1-hour 4K video at 9:00 AM.
  Tweet at 9:05 AM: viral. 1M users click link.
  Transcoding time: 4K, 1 hour = ~45 minutes on 10 parallel workers.

  Users at 9:05 AM: video "not ready" → ERROR or "processing, please wait"
  Audience lost: most don't come back.

  STRATEGIES:

  1. PRIORITY QUEUE:
     Detect viral indicators: link shared 100K times in 5 minutes → bump to high-priority queue.
     High-priority queue: 10× more workers → 45 minutes → 5 minutes.

  2. LOW-QUALITY FIRST (progressive transcoding):
     Transcode 360p first (fastest) → make video available immediately at 360p.
     Continue: 480p, 720p, 1080p, 4K in the background.

     Priority order: 360p (2 minutes) → video available → 480p → 720p → 1080p → 4K.
     User experience: video plays immediately at 360p → quality improves as higher variants become available.

     HLS adaptive: manifest updated as each quality becomes available.
     ABR player: switches to higher quality automatically when manifest is updated.

  3. RESERVE TRANSCODING CAPACITY FOR HOT CONTENT:
     Monitor upload velocity: if >100 shares/minute within first 5 minutes → viral.
     Reserve GPU transcoding workers (EC2 P-class) for viral content.
     Regular content: CPU transcoding (cheaper). Viral: GPU (10× faster).

  4. EDGE TRANSCODING (experimental, Cloudflare Stream):
     Upload raw segments to CDN edge for immediate low-quality delivery.
     Full transcoding: runs asynchronously in background.
     Viewer: starts watching 360p from CDN in < 60 seconds of upload.
```

---

### 🔗 Related Keywords

- `CDN` — delivers video segments from edge nodes close to viewer (< 10ms vs > 100ms from origin)
- `Object Storage` — S3 stores video segments durably and cheaply; integrated with CDN
- `Adaptive Bitrate Streaming` — player algorithm (HLS, DASH) switches quality per segment
- `Transcoding` — converting raw video to multiple quality variants and HLS/DASH segments

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Transcode to multiple ABR quality levels; │
│              │ distribute segments via CDN edge nodes    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Video-on-demand; live streaming; adaptive │
│              │ quality for variable network conditions   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long segments (poor seek/quality switch); │
│              │ no low-quality variant for poor networks  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pressure-adaptive water valve — CDN      │
│              │  stores water locally; valve adjusts      │
│              │  flow to match pipe pressure."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CDN Architecture → Object Storage         │
│              │ → DRM and Content Protection              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Netflix uses "per-title encoding" — instead of fixed bitrates per resolution, they analyse each video's complexity (a cartoon requires less bitrate than a fast action scene at the same quality) and encode at an optimal bitrate for that specific title. How would you design the per-title encoding pipeline? What inputs does the analysis step need? What output does it produce? How does this affect the CDN manifest and the CDN cache (since bitrates are no longer standardised across all videos)?

**Q2.** Design the video seek optimisation for a 2-hour movie: a user jumps from 00:05:00 to 01:45:00. With 4-second HLS segments, the player needs segment number 1575 (approximately). Describe: (a) how the player calculates which segment to request; (b) how the initial buffering at the new seek position differs from regular playback (the buffer is empty — player needs to download at least 3 segments before starting playback); (c) how CDN pre-fetching could be used if you know a user has been seeking frequently (e.g., they're skipping through the video — common for tutorial content).
