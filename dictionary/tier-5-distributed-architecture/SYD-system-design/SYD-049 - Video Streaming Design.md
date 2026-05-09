---
id: SYD-049
title: Video Streaming Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-023
used_by:
related: SYD-024, SYD-027
tags:
  - architecture
  - advanced
  - distributed
  - performance
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /syd/video-streaming-design/
---

# SYD-049 - Video Streaming Design

⚡ TL;DR - Video streaming encodes files into multiple quality
renditions, segments them into small chunks, distributes chunks
via CDN, and adapts quality dynamically to available bandwidth.

| Field           | Detail                            |
| :-------------- | :-------------------------------- |
| **Depends on:** | SYD-023 - Geo-Replication        |
| **Used by:**    | -                                 |
| **Related:**    | SYD-024, SYD-027                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before adaptive streaming, video was delivered as a single file.
The player had to buffer enough of the file before starting
playback. On slow connections, users waited minutes before the
first frame appeared. On congested networks, playback paused to
rebuffer mid-stream.

**THE BREAKING POINT:**
Global audiences on heterogeneous networks (3G, WiFi, fiber) with
varying device capabilities (4K TV, mobile phone) cannot all
receive the same fixed-bitrate file and have a good experience.
A file sized for 4K streaming causes constant rebuffering on 3G.

**THE INVENTION MOMENT:**
The core insight: pre-encode the same content at multiple bitrates
(renditions), split each rendition into small time-based segments
(2-10 seconds), and let the player dynamically switch between
renditions based on real-time bandwidth measurement. A manifest
file tells the player what renditions exist and where to fetch
each segment.

**EVOLUTION:**
Video streaming evolved from downloading entire files (RealPlayer,
1995) through progressive download to adaptive bitrate streaming
(ABR). YouTube (2005) demonstrated internet-scale video delivery
was possible with commodity hardware and CDN caching. Netflix
(2007-2012) pioneered ABR streaming with DASH and HLS formats,
then built Open Connect - their own CDN embedded in ISP networks.
The engineering challenge evolved from bandwidth efficiency to
per-viewer adaptation, then to latency reduction for live
streaming, and now to per-viewer ML-driven quality optimisation.
Video streaming accounts for approximately 70% of all internet
downstream bandwidth.

---

### 📘 Textbook Definition

**Video Streaming Design** is a system design problem centred on
delivering large video files to global audiences at varying
network conditions, using transcoding pipelines, adaptive bitrate
(ABR) algorithms, content delivery networks (CDN), and segment-
based playback protocols such as HLS and MPEG-DASH.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Encode video at multiple qualities, cut it into small segments,
cache segments near the viewer, and switch quality in real time.

**One analogy:**

> A highway with multiple speed lanes: slow drivers stay in the
> slow lane; fast drivers move to the fast lane. Traffic (ABR
> algorithm) continuously picks the best lane for current
> conditions without stopping.

**One insight:**
Segments are the unit of everything in streaming: CDN caches
segments, ABR switches between renditions at segment boundaries,
and players buffer segments ahead to absorb network jitter.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Video playback requires continuous, uninterrupted frame
   delivery at a fixed frame rate (24/30/60 fps).
2. Network bandwidth is variable and unpredictable.
3. Video quality (resolution, bitrate) can be varied between
   segments without interrupting playback.
4. Segments cached near the viewer reduce both latency and
   origin server load.

**DERIVED DESIGN:**
Invariants 2 and 3 together derive ABR: vary quality dynamically.
Invariant 4 derives CDN distribution. Invariant 1 derives the
need to buffer ahead (2-5 segments) to absorb bandwidth drops.
The segment size (2-10 seconds) is a trade-off: shorter segments
enable faster quality adaptation; longer segments reduce manifest
overhead but slow adaptation.

**THE TRADE-OFFS:**
**Gain:** Smooth playback on variable networks; global scalability
via CDN; lower origin server load.
**Cost:** Storage multiplication (N renditions x total content);
transcoding pipeline complexity; encoding cost at ingest.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Multi-rendition encoding; CDN distribution;
bandwidth estimation in the player; segment-boundary switching.
**Accidental:** Segment format fragmentation (HLS vs DASH vs
Smooth Streaming); per-codec transcoding duplication; DRM key
management complexity.

---

### 🧪 Thought Experiment

**SETUP:** You are building a video streaming service for 10
million users worldwide. You decide to skip multi-rendition
encoding and serve a single 1080p video file to all users.

**WHAT HAPPENS WITHOUT IT:**
A user on a 500 kbps 3G connection starts loading your 8 Mbps
1080p file. They must buffer 16x real-time. The player either
stalls immediately or shows a loading spinner for 30+ seconds.
70% of users abandon before the first frame. Users on fiber
receive excellent quality, but only 10% of your global audience
has fiber. Serving one rendition optimises for 10% of users.

**WHAT HAPPENS WITH IT:**
The same 3G user receives a 240p rendition at 300 kbps - just
within their bandwidth. Playback starts in 3 seconds. If signal
improves (they walk indoors to WiFi), the player switches to 720p
seamlessly at the next segment boundary. The fiber user gets 4K.
Each user receives the best quality their network can sustain.

**THE INSIGHT:**
The goal is not "best quality" but "best quality for this
connection right now". ABR converts a fixed constraint (file
quality) into a dynamic variable that the system continuously
optimises.

---

### 🧠 Mental Model / Analogy

> An airline booking system that dynamically upgrades or downgrades
> your seat based on real-time availability: your seat class
> changes at each layover (segment boundary) without your journey
> being interrupted.

Element mapping:
- Seat class = video rendition (240p / 720p / 1080p / 4K)
- Layover = segment boundary (every 4 seconds)
- Flight availability = available network bandwidth
- Upgrade/downgrade decision = ABR algorithm
- Airport lounges worldwide = CDN edge nodes

Where this analogy breaks down: airlines change your seat once;
ABR changes quality at every segment boundary, potentially
hundreds of times per viewing session.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Video streaming adjusts video quality automatically based on your
internet speed, so you get smooth playback even on a slow
connection - just at lower resolution.

**Level 2 - How to use it (junior developer):**
Use FFmpeg to transcode a video to multiple bitrates. Use HLS
or DASH to generate a manifest file and segments. Upload segments
to S3. Serve via CloudFront CDN. The client player handles ABR
automatically using a library like hls.js or dash.js.

**Level 3 - How it works (mid-level engineer):**
The transcoding pipeline converts the original into renditions
(e.g., 240p/500kbps, 480p/1Mbps, 720p/3Mbps, 1080p/8Mbps).
Each rendition is split into 4-second segments. A master manifest
(`.m3u8` for HLS) lists all renditions with their bandwidth.
A per-rendition manifest lists all segments. The player measures
throughput of the last segment download, computes a buffer health
metric, and selects the next rendition using an ABR algorithm.
Segments are cached at CDN edge nodes closest to the viewer.

**Level 4 - Why it was designed this way (senior/staff):**
Segment-based delivery decouples CDN caching from video duration:
a CDN can cache individual 4-second segments, not entire multi-GB
files. This makes CDN cache hit rates extremely high (popular
content has thousands of viewers sharing the same cached segments).
ABR runs entirely client-side in most implementations, eliminating
the need for the server to know each viewer's bandwidth. Netflix's
BOLA (Buffer Occupancy Based Lyapunov Algorithm) optimises for
buffer health rather than raw throughput, preventing rebuffering
events even on throughput-variable connections.

**Expert Thinking Cues:**
- "What is the cache hit rate for popular content?" - extremely
  high if segments are uniform across renditions.
- "Who runs the ABR algorithm?" - the player, not the server.
- "What is the failure mode of aggressive ABR?" - quality
  oscillation (rapid switching up and down).

---

### ⚙️ How It Works (Mechanism)

```
Ingest pipeline:
  Original file
    -> Transcoder (FFmpeg/AWS MediaConvert)
       -> 240p, 480p, 720p, 1080p, 4K renditions
          -> Segmenter (4-sec chunks + manifests)
             -> S3 (origin)
                -> CDN (CloudFront/Akamai/Open Connect)

Playback:
  Player fetches master manifest
  -> Selects initial rendition
  -> Downloads first segment
  -> Measures download throughput
  -> ABR algorithm selects next rendition
  -> Downloads next segment from CDN edge
  -> Repeat every 4 seconds
```

**ABR Algorithm Decision (simplified BOLA):**
Buffer occupancy < 10s: downgrade rendition.
Buffer occupancy 10-30s: maintain rendition.
Buffer occupancy > 30s: upgrade rendition if bandwidth supports.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
+----------+   upload   +----------+   +----------+
| Creator  |----------->|Transcode |-->|  S3      |
+----------+            | Pipeline |   | (origin) |
                        +----------+   +----+-----+
                                            |
                                       CDN push/pull
                                            |
                                   +--------+--------+
                                   |    CDN Edge     |
                                   | (near viewer)   |
                                   +--------+--------+
                                            |
                                       segment fetch
                                            |
+----------+  manifest  +----------+        |
|  Player  |<-----------|CDN Edge  |<-------+
|  (ABR)   |  segments  +----------+
+----------+                    <- YOU ARE HERE (playback)
```

**FAILURE PATH:**
- CDN edge miss: request falls through to origin (slower but
  works). High miss rate = origin overload.
- Transcoding failure: video unavailable; retry pipeline.
- ABR over-optimistic: player requests higher rendition than
  network supports; buffer drains; rebuffer event.

**WHAT CHANGES AT SCALE:**
- Popular content: CDN cache hit rates >99%; origin rarely hit.
- Long-tail content: low cache hit rate; origin serves most
  requests; CDN less effective.
- Concurrent launches: thundering herd at CDN edge for new
  popular content; mitigate with pre-warming.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
- Each viewer independently fetches segments; no server-side
  state per viewer for on-demand streaming.
- Live streaming adds real-time ingest latency: segments must be
  available at CDN within seconds of being recorded.
- DRM adds key server round-trip per viewer per content item.

---

### 💻 Code Example

**BAD - Single rendition, no CDN:**

```python
# Server directly streams the single 1080p file
# No adaptation, no CDN, no segments
@app.route('/video/<video_id>')
def stream_video(video_id):
    path = f"/storage/{video_id}/1080p.mp4"
    return send_file(path, mimetype='video/mp4')
    # Problems: no adaptation, origin overload at scale,
    # all bandwidth from your servers
```

**GOOD - Manifest + CDN + ABR:**

```python
@app.route('/video/<video_id>/manifest.m3u8')
def video_manifest(video_id):
    # Return pre-generated HLS master manifest from S3
    # Player handles ABR client-side
    cdn_base = f"https://cdn.example.com/{video_id}"
    manifest = generate_master_manifest(
        video_id,
        renditions=[
            (240, 400_000),
            (480, 1_000_000),
            (720, 3_000_000),
            (1080, 8_000_000),
        ],
        cdn_base=cdn_base
    )
    return manifest, 200, {'Content-Type': 'application/vnd.m3u8'}

# Player fetches: /video/abc/manifest.m3u8
# Player picks rendition based on bandwidth
# Player fetches segments from CDN directly
# No further origin involvement for segments (CDN serves)
```

**How to test / verify correctness:**
- Unit: test manifest generation for correct rendition URLs.
- Integration: throttle network to 500 kbps; verify player
  switches to 240p rendition within 2 segment cycles.
- Load: simulate 10K concurrent viewers; verify CDN handles
  without origin overload (check origin request rate).

---

### ⚖️ Comparison Table

| Concern           | HLS (Apple)         | MPEG-DASH           |
| ----------------- | ------------------- | ------------------- |
| Segment format    | MPEG-TS / fMP4      | fMP4                |
| Platform support  | Native iOS/Safari   | Chrome/Firefox/Edge |
| Latency (live)    | 10-30s (std)        | 2-8s (low-latency)  |
| ABR flexibility   | Limited by spec     | Fully customisable  |
| CDN compatibility | Universal           | Universal           |

| Approach       | Use when                         |
| -------------- | -------------------------------- |
| HLS            | Apple device support required    |
| DASH           | Cross-platform, adaptive quality |
| Progressive DL | Short clips, no adaptation needed|
| WebRTC         | Live, sub-1s latency required    |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "ABR maximises resolution" | ABR maximises playback continuity. It will downgrade quality to prevent rebuffering, even if bandwidth could technically support higher quality. |
| "CDN solves all scaling problems" | CDN excels for popular content (high cache hit rates). Long-tail content has low hit rates and still stresses the origin. |
| "Longer segments are better" | Longer segments (10+ seconds) slow ABR adaptation. A network change takes longer to detect and adapt to. 4-6 seconds is the common sweet spot. |
| "Live streaming is just on-demand with no pre-encoding" | Live streaming has fundamentally different pipeline constraints: real-time encoding, segment availability within seconds, and no pre-warming is possible. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Thundering herd at CDN on launch**

**Symptom:** Major title launches at midnight. First 2 minutes of
content get massive cache misses; origin servers become
overwhelmed; initial viewers experience long start times.

**Root Cause:** CDN cache is cold for the new content. Millions of
simultaneous requests for the first segments miss the cache and
hit origin simultaneously.

**Diagnostic:**
```bash
# Check CDN origin request rate at launch vs steady state
aws cloudwatch get-metric-statistics   --namespace AWS/CloudFront   --metric-name Requests   --dimensions Name=DistributionId,Value=$DIST_ID   --start-time $LAUNCH_TIME --end-time $PLUS_5MIN   --period 60 --statistics Sum
```

**Fix:**

BAD: Launch content cold; let CDN warm organically.
GOOD: Pre-warm CDN by proactively fetching popular segments
to all edge nodes 30 minutes before launch using CDN warming
API or a synthetic request generator.

**Prevention:** Pre-warm CDN before launch; use soft-launch with
small cohort to warm cache before full release.

---

**Failure Mode 2: ABR quality oscillation**

**Symptom:** Video quality constantly switches between 480p and
1080p every few seconds, causing visible quality flickering for
the viewer.

**Root Cause:** ABR algorithm is too aggressive in upgrading
quality (switches to 1080p on brief bandwidth spike) then must
immediately downgrade when the spike subsides.

**Diagnostic:**
```bash
# In browser console (hls.js)
hls.on(Hls.Events.LEVEL_SWITCHING, (event, data) => {
  console.log('Switch to level:', data.level,
    'at time:', video.currentTime);
});
# Frequent LEVEL_SWITCHING events = oscillation
```

**Fix:**

BAD: Use throughput-only ABR (switch up on any bandwidth spike).
GOOD: Use buffer-occupancy ABR (BOLA): upgrade only when buffer
is comfortably full; weight downgrade more aggressively than
upgrade to prevent oscillation.

**Prevention:** Set upgrade hysteresis (require N consecutive
segments at high bandwidth before upgrading); tune ABR for
content type (sports: smooth > quality; film: quality > smooth).

---

**Failure Mode 3: Live streaming lag spike**

**Symptom:** Live streaming latency spikes from 5 seconds to 60+
seconds for all viewers simultaneously.

**Root Cause:** Transcoder pipeline falls behind real-time: slow
encoding causes segments to become available late; CDN serves
stale manifest pointing to non-existent future segments; players
stall waiting.

**Diagnostic:**
```bash
# Check transcoder queue depth
aws mediaconvert list-jobs --status PROGRESSING   --query 'Jobs[*].{Id:Id,Progress:JobPercentComplete}'
# If progress < 95% for a LIVE job = falling behind
```

**Fix:**

BAD: Single transcoder instance; no monitoring on segment
availability lag.
GOOD: Monitor segment availability delay (time from capture to
CDN availability); auto-scale transcoder fleet when lag > 2s;
use GPU-accelerated encoding for real-time throughput headroom.

**Prevention:** Provision transcoder capacity at 2x expected
peak; set alerting on segment lag > 3 seconds; test with
simulated bitrate spikes in staging.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-023 - Geo-Replication]] - CDN caching is geo-replication
  applied to video segments at edge nodes worldwide

**Builds On This (learn these next):**
- [[SYD-024 - Multi-Region Architecture]] - deployment pattern
  for global video CDN infrastructure
- [[SYD-027 - Capacity Planning]] - video is the highest-bandwidth
  workload to capacity plan in any consumer system

**Alternatives / Comparisons:**
- [[SYD-024 - Multi-Region Architecture]] - broader deployment
  pattern that video CDN is an implementation of
- [[SYD-048 - Chat System Design]] - contrasting real-time design
  (low latency + small payloads vs high throughput + large files)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------------+
| WHAT IT IS  | Multi-rendition segment-based adaptive      |
|             | video delivery via CDN                      |
+-----------------------------------------------------------+
| PROBLEM     | Variable bandwidth + huge files = constant  |
|             | rebuffering for some users                  |
+-----------------------------------------------------------+
| KEY INSIGHT | Segments are the unit: encode, cache, and   |
|             | switch quality at segment boundaries        |
+-----------------------------------------------------------+
| USE WHEN    | Delivering video to global audiences at     |
|             | varying network conditions                  |
+-----------------------------------------------------------+
| AVOID WHEN  | Short clips where progressive download is   |
|             | simpler (< 30 seconds of content)           |
+-----------------------------------------------------------+
| TRADE-OFF   | Storage x N renditions vs smooth playback   |
|             | on all network conditions                   |
+-----------------------------------------------------------+
| ONE-LINER   | Transcode to multiple quality levels,       |
|             | segment, cache at CDN, let player adapt     |
+-----------------------------------------------------------+
| NEXT EXPLORE| Multi-Region Architecture (SYD-024)        |
+-----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Encode at multiple bitrates; split into 4-second segments.
2. CDN caches segments close to viewers - not the full file.
3. ABR runs in the player; the server does not control quality.

**Interview one-liner:** "Video streaming encodes multiple bitrate
renditions, segments them into small chunks cached at CDN edge
nodes, and uses adaptive bitrate algorithms in the player to
switch quality dynamically based on available bandwidth."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Segment, cache, and adapt. When content is large and networks are
variable, the solution is to segment content into uniform chunks,
cache chunks close to the consumer, and adapt delivery rate to
available capacity. This three-part strategy is not unique to
video.

**Where else this pattern appears:**
- **Software update delivery:** macOS and Windows updates are
  chunked into segments and delivered via CDN with delta-only
  downloads after the initial version - the same segment-and-cache
  pattern.
- **Podcast streaming:** RSS audio files are served via CDN with
  HTTP range request support, enabling the player to fetch and
  buffer ahead without downloading the full file.
- **Kafka streaming:** Producers write to partitioned log
  segments; consumers read at their own pace from the nearest
  replica - adaptive throughput via partition assignment mirrors
  ABR's adapt-to-consumer-pace model.

---

### 💡 The Surprising Truth

Video streaming's biggest engineering challenge is not bandwidth
but time synchronisation for live events. Live streaming must
deliver video frames to millions of viewers within seconds of each
other (for sports, financial events, elections). The difference
between a 2-second and a 10-second delay determines whether
viewers can discuss the same event in real time on social media.
Achieving sub-5-second live streaming latency at scale requires
bypassing traditional CDN caching (which introduces delays) and
using low-latency protocols (LL-HLS, WebRTC). Most streaming
platforms quietly accept 20-30 second delays for "live" events
because true low latency at scale is significantly more expensive
- and most viewers do not notice the difference unless they are
also watching the same event on broadcast TV.

---

### 🧠 Think About This Before We Continue

**Q1.** What hurts more in your product: lower resolution or more
buffering?

*Hint:* Think about what product the user is actually consuming -
sports streaming (low latency > resolution), documentary (resolution
> latency), user-generated content (buffering tolerance varies).
Explore whether the answer changes by content type and whether the
product should offer user-configurable quality preferences.

**Q2.** How would live video design differ from on-demand video
design?

*Hint:* Think about the fundamental difference: on-demand content
has the complete file available before any viewer starts watching
(pre-encode, pre-upload to CDN), while live content has only the
last few seconds available at any moment. Explore what changes in
the encoding pipeline, CDN strategy, and error recovery when
pre-caching is impossible.

**Q3 (Scale):** A popular show launches and 2 million users start
streaming the same episode simultaneously at exactly 12:01 AM.
Your CDN has a 5-minute TTL on video segments. Design a
pre-warming strategy that ensures smooth playback at launch.

*Hint:* Think about what happens when 2 million cache misses hit
the origin simultaneously for the same segments. Explore how
pre-warming (distributing popular content to edge nodes before
launch) and staggered release (soft launch with a small cohort at
11:59 PM) prevent the thundering herd at the CDN edge.
