---
layout: default
title: "Data Compression (gzip, snappy, zstd, lz4)"
parent: "Data Fundamentals"
nav_order: 508
permalink: /data-fundamentals/data-compression/
number: "508"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Binary Formats (Avro, Parquet, ORC, Protobuf), Columnar vs Row Storage
used_by: Parquet, ORC, Avro, Kafka, Data Pipeline Performance
tags:
  - data
  - storage
  - performance
  - intermediate
---

# 508 — Data Compression (gzip, snappy, zstd, lz4)

`#data` `#storage` `#performance` `#intermediate`

⚡ TL;DR — Data compression algorithms reduce storage size and I/O bandwidth at the cost of CPU; Snappy and LZ4 prioritise speed; gzip and Zstd prioritise ratio; the right choice depends on latency vs. storage trade-offs.

| #508 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Binary Formats (Avro, Parquet, ORC, Protobuf), Columnar vs Row Storage | |
| **Used by:** | Parquet, ORC, Avro, Kafka, Data Pipeline Performance | |

---

### 📘 Textbook Definition

**Data compression** is the process of encoding data using fewer bits than the original representation. Lossless compression algorithms used in data engineering preserve exact data fidelity. Key algorithms: **gzip** (DEFLATE/LZ77+Huffman — high ratio, slow); **Snappy** (Google, developed for Hadoop — fast, moderate ratio, not streaming-friendly); **LZ4** (extremely fast compression/decompression — optimal for low-latency pipelines); **Zstd** (Facebook's Zstandard — tunable ratio/speed, superior to gzip in most benchmarks). Columnar formats (Parquet, ORC) apply both column encoding (dictionary, RLE) and file-level compression, achieving much higher ratios than row-based formats.

### 🟢 Simple Definition (Easy)

Compression squeezes data into smaller files. LZ4 is the fastest but saves less space. Zstd saves the most space while being reasonably fast. Pick based on whether you care more about speed or storage cost.

### 🔵 Simple Definition (Elaborated)

Every byte stored in a data lake costs money and every byte transferred over a network costs time. Compression reduces both. The trade-off is CPU: compressing and decompressing takes cycles. For hot pipelines (real-time streaming, fast ETL), use LZ4 or Snappy — they compress/decompress in microseconds with 2–3× compression ratio. For cold storage (archival, bulk analytics), use Zstd level 3–19 — it achieves 5–10× compression ratio at the cost of more CPU. gzip is the legacy standard, often beaten by Zstd on both ratio AND speed in modern benchmarks.

### 🔩 First Principles Explanation

**How compression works (conceptually):**

```
LZ-family (LZ77, LZ4, Snappy):
  Find repeated patterns in recent data → replace with back-references
  "apple banana apple cherry apple" →
  "apple banana <5 chars back, 5 len> cherry <12 chars back, 5 len>"
  Fast because: look-ahead window is small; no entropy coding

gzip (DEFLATE = LZ77 + Huffman):
  LZ77 finds repeated strings
  Huffman assigns short codes to frequent symbols
  Better ratio because: two-pass compression, entropy coding
  Slower because: two passes, more CPU per byte

Zstd:
  LDM (Long Distance Matching) + Huffman/FSE entropy coding
  Tunable levels 1–22 (or -1 to -7 ultra-fast)
  Level 3: comparable to gzip with 3–5× higher speed
  Level 19: better ratio than gzip on most datasets

Dictionary compression (columnar advantage):
  Column values often repeat: "US", "UK", "DE", "US", "US"...
  Dictionary: {0:US, 1:UK, 2:DE}
  Encoded: [0, 1, 2, 0, 0] → then LZ4/Snappy on the tiny encoded ints
  → Much higher ratios than row-based compression
```

**Benchmark comparison (typical structured data):**

```
Algorithm  Compress Speed  Decompress Speed  Ratio  Use Case
────────────────────────────────────────────────────────────────
LZ4        500 MB/s        2000 MB/s         2.1×   Real-time streaming
Snappy     400 MB/s        1500 MB/s         2.1×   Hadoop/Spark default
Zstd(3)    400 MB/s        1000 MB/s         3.5×   Balanced (recommended)
Zstd(9)    100 MB/s         800 MB/s         4.5×   Storage-optimised
gzip(6)     50 MB/s         200 MB/s         3.5×   Legacy; HTTP transfer
gzip(9)     20 MB/s         200 MB/s         4.0×   Maximum ratio legacy
brotli      30 MB/s         200 MB/s         5.0×   Web/browser transfer

+column encoding (Parquet/ORC):
Zstd(3) on Parquet    ↑ additional 2-5× vs row format with same codec
```

**Codec selection by use case:**

```
Use case                     Recommended     Reason
──────────────────────────────────────────────────────────────
Kafka topics                 lz4, snappy     Low latency decompression per msg
Parquet files (Spark ETL)    snappy, zstd    Balance reads (many queries)
Parquet cold storage         zstd(9+)        Maximise ratio for archival
Avro in Kafka               snappy, lz4     Fast per-record decompression  
REST API responses           gzip, brotli   Browser / HTTP client support
Network file transfer        zstd            Best ratio/speed overall
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT compression:
- 1 TB raw CSV → 1 TB on disk → 1 TB network transfer → slow.
- At $0.023/GB/month S3: 1 PB = $23,000/month. With Zstd: ~$5,000/month.
- Columnar format + Zstd: 10×+ reduction → reduces S3 reads → reduces Spark cost.

WITH compression:
→ Parquet + Snappy: typical 5-10× smaller than raw CSV.
→ Parquet + Zstd: 8-15× smaller than raw CSV on structured data.
→ Less data transferred = faster queries = lower Spark scan costs.

### 🧠 Mental Model / Analogy

> Compression algorithms are like different types of luggage packing. LZ4 is like cramming things in quickly — not perfectly organised but incredibly fast to pack and unpack. gzip is like a meticulous packer who folds everything perfectly — takes longer but uses far less space. Zstd is the modern smart packer — nearly as compact as gzip but nearly as fast as LZ4. And columnar dictionary encoding is like packing a suitcase full of identical T-shirts by writing "50× red T-shirt" instead of packing 50 shirts individually.

### ⚙️ How It Works (Mechanism)

**Parquet compression config in Spark:**

```python
# Per-column compression (Parquet page-level)
spark.conf.set("spark.sql.parquet.compression.codec", "zstd")
# Options: none, snappy, lz4, zstd, gzip, brotli, lzo

# Zstd compression level (1-22, default 3)
spark.conf.set("parquet.zstd.level", "3")

# Write with explicit codec
df.write.option("compression", "zstd").parquet("s3://bucket/data/")
```

**Avro/Kafka compression:**

```java
// Kafka producer: compress all messages with LZ4
Properties props = new Properties();
props.put("compression.type", "lz4"); // or snappy, gzip, zstd
// LZ4 preferred: lowest latency per message, good ratio
```

### 🔄 How It Connects (Mini-Map)

```
Raw columnar data (Parquet/ORC column pages)
        ↓ compressed by
Compression Codec ← you are here
  (LZ4 / Snappy / Zstd / gzip)
        ↓ stored in
Parquet/ORC files on S3 / HDFS
        ↓ affects
Query performance | Storage cost | Network transfer time
        ↓ applied also in
Kafka topics | REST API responses | HTTP (gzip/brotli)
```

### 💻 Code Example

```python
# Benchmark: compare Parquet sizes with different codecs
import time

for codec in ["none", "snappy", "lz4", "zstd", "gzip"]:
    t0 = time.time()
    df.write.mode("overwrite") \
            .option("compression", codec) \
            .parquet(f"s3://bucket/bench/{codec}/")
    write_time = time.time() - t0

    # Check file sizes
    files = spark.conf.get(
        f"s3://bucket/bench/{codec}/")
    print(f"{codec}: write={write_time:.1f}s, size=TBD")

# Typical results for 100M row event table:
# none:    1.0s write,  8.2 GB
# snappy:  1.4s write,  1.8 GB (4.6× smaller)
# lz4:     1.3s write,  1.9 GB (4.3× smaller)
# zstd:    1.6s write,  1.2 GB (6.8× smaller)
# gzip:    5.2s write,  1.3 GB (6.3× smaller, 3× slower write)
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More compression ratio always means better | High-ratio codecs (gzip level 9) can make read-heavy analytics slower since decompression is CPU-intensive. Snappy/LZ4 are often faster end-to-end. |
| Snappy is always best for Parquet | Snappy was the Hadoop-era default but Zstd level 3 typically provides better ratio with similar decompression speed on modern CPUs. |
| Compression is only for storage savings | Compression can actually IMPROVE query performance by reducing I/O bandwidth (data transfer from S3/disk). Reading 1 GB compressed is faster than 5 GB uncompressed if CPU is faster than I/O. |
| gzip and Zstd produce similar results | Zstd at level 3 typically equals gzip at level 6 in ratio, while being 5× faster to compress and 3× faster to decompress. |

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ Fast+streaming:  LZ4, Snappy → Kafka, real-time ETL    │
│ Balanced:        Zstd(3)     → Recommended default     │
│ Max ratio:       Zstd(9-19)  → Cold storage/archival   │
│ Legacy/HTTP:     gzip        → APIs, browser, legacy   │
├────────────────────────────────────────────────────────┤
│ ONE-LINER │ "LZ4=speed, gzip=ratio, Zstd=both."       │
└────────────────────────────────────────────────────────┘
```

