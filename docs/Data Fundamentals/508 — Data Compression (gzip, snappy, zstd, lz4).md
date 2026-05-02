---
layout: default
title: "Data Compression (gzip, snappy, zstd, lz4)"
parent: "Data Fundamentals"
nav_order: 508
permalink: /data-fundamentals/data-compression/
number: "0508"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Binary Formats, Columnar vs Row Storage, Data Types
used_by: Parquet, ORC, Avro, Data Lake, Big Data
related: Parquet, Avro, Binary Formats, Serialization Formats, Columnar vs Row Storage
tags:
  - dataengineering
  - intermediate
  - performance
  - bigdata
  - networking
---

# 508 — Data Compression (gzip, snappy, zstd, lz4)

⚡ TL;DR — Data compression trades CPU time for smaller byte footprint — the right algorithm depends on whether speed or size matters more for your pipeline.

| #508 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Binary Formats, Columnar vs Row Storage, Data Types | |
| **Used by:** | Parquet, ORC, Avro, Data Lake, Big Data | |
| **Related:** | Parquet, Avro, Binary Formats, Serialization Formats, Columnar vs Row Storage | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Spark job writes 500 GB of Parquet data to S3 every hour.
Without compression, the S3 bill for storage is $15/TB/month
× 500 GB/hour × 730 hours/month = ~$5,475/month for one table.
Network transfer between Spark nodes and S3 saturates at 10 GB/s.
The job is I/O bound — CPUs are idle while data flows to/from S3.

**THE BREAKING POINT:**
At petabyte scale, every uncompressed byte is a recurring cloud
storage and network cost. Data pipelines that process 10 TB/day
uncompressed would process 1–3 TB/day compressed — with the same
cluster. The compute cost of compression (< 10% CPU overhead for
fast codecs like Snappy) pays back thousands-fold in I/O reduction.

**THE INVENTION MOMENT:**
This is exactly why compression codecs for data formats were
created. Different codecs make different trade-offs between
compression ratio (smaller = higher ratio) and throughput
(faster = higher throughput). The right codec depends on your
workload's bottleneck: is it storage cost (use GZIP/Zstd), or
is it CPU (use LZ4/Snappy), or both?

---

### 📘 Textbook Definition

**Data compression** is the process of encoding data using fewer
bits than the original representation by exploiting patterns,
redundancy, and statistical regularities in the data. Lossless
compression codecs (used in data pipelines) guarantee perfect
reconstruction of the original data. **gzip** uses DEFLATE
(LZ77 + Huffman) — high ratio, moderate speed. **Snappy** (Google)
prioritises decompression throughput: moderate ratio, very fast.
**Zstandard (zstd)** is a modern codec with configurable
compression level — Snappy's speed at levels 1–3, gzip's ratio
at levels 6–15. **LZ4** is the fastest practical lossless codec —
extremely fast but lower ratio. In columnar data formats (Parquet,
ORC), compression is applied per-column-chunk AFTER encoding,
compounding the gains: dictionary-encoded column + Snappy
compression together achieve 5–20× the compression of raw text.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Compression finds patterns in data and stores those patterns
instead of the raw bytes — taking up less space.

**One analogy:**

> Imagine writing a letter that says "the the the the the" 100
> times. Instead of writing all 500 characters, you could write
> " 'the' × 100" — 8 characters instead of 500. That's
> run-length encoding, the simplest form of compression.
> Modern codecs apply dozens of such tricks simultaneously.

**One insight:**
For data pipelines, compression is not about archiving — it's
about throughput. Compressed reads from S3 are faster than
uncompressed reads because the bottleneck is network bandwidth
(10 Gbps) not CPU decompression (100+ Gbps throughput for LZ4).
Compressing data means less bytes travel over the wire — so the
pipeline runs faster even accounting for the CPU cost of
decompression.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Real-world data has redundancy: repeated words, sequential
   numbers, clusters of similar values.
2. Exploiting redundancy requires CPU time (for both compression
   and decompression).
3. Reducing bytes reduces I/O time proportionally.

**HOW COMPRESSION ALGORITHMS WORK:**

*LZ-family (gzip, Snappy, Zstd, LZ4 all use LZ variants):*
Find repeated byte sequences in a sliding window. Replace the
repeated occurrence with a (distance, length) back-reference.
`"the quick brown fox the quick"` → store "the quick" once,
then at second occurrence: `(back 20 bytes, copy 9 bytes)`.
LZ algorithms differ in window size, hash function quality,
and back-reference encoding efficiency.

*Huffman coding (used in gzip):*
Build a frequency table of all byte values. Assign shorter bit
codes to frequent values. `'e'` (most common English letter) →
3 bits instead of 8 bits. `'z'` (rare) → 12 bits. On average,
saves 30–40% over raw ASCII.

*gzip (DEFLATE = LZ77 + Huffman):*
Best ratio among the four, slowest compression speed. ~3:1 ratio
typical. Decompression is fast (1 pass, no search).

*Snappy (Google, 2011):*
LZ variant with 32-byte hash chains. Does NOT implement Huffman.
Because it skips Huffman, it's 3–5× faster to compress than gzip
at 60–70% of the compression ratio. Google's priority: Snappy
must be fast enough that it cannot be the bottleneck on any
pipeline. Designed for Hadoop where CPUs were the scarce resource.

*LZ4 (2011):*
LZ variant with extremely simple hash function. Fastest practical
codec — 400–700 MB/s compression, 2000–4000 MB/s decompression.
Lower ratio than Snappy. Use when any CPU overhead is unacceptable.

*Zstandard (zstd, Facebook, 2016):*
LZ77 + ANS (Asymmetric Numeral Systems) entropy coding. Level 1:
slightly better than Snappy at near-Snappy speed. Level 3:
same ratio as gzip at 2× gzip speed. Level 9+: better than gzip,
3× slower. Tuneable: the best general-purpose codec since 2018.

**THE TRADE-OFFS:**

| Codec | Compression Speed | Decompression Speed | Ratio | Best For |
|---|---|---|---|---|
| gzip | 20–50 MB/s | 250 MB/s | ~3:1 | Cold storage, small files |
| Snappy | 200–500 MB/s | 500–600 MB/s | ~2:1 | Hot Parquet, Spark-to-Spark |
| Zstd (L1) | 200-400 MB/s | 600-800 MB/s | ~2.5:1 | Default for new pipelines |
| Zstd (L9) | 30-80 MB/s | 600-800 MB/s | ~3.5:1 | Long-term archive |
| LZ4 | 400-700 MB/s | 2000-4000 MB/s | ~1.5:1 | In-memory shuffle, realtime |

---

### 🧪 Thought Experiment

**SETUP:**
A Parquet table stores `status` column with values
`['COMPLETE', 'PENDING', 'CANCELLED']` — 3 distinct values
across 100 million rows. After dictionary encoding: each value
becomes 0, 1, or 2 (1 byte). Then you apply compression.

**WITHOUT COMPRESSION:**
After dictionary → 100M × 1 byte = 100 MB for status column.
If data is unsorted: bytes are `[0,2,1,0,2,1,0,0,2,1...]` —
pseudo-random. gzip and Snappy achieve ~1.2:1 ratio on random
bytes = 83 MB.

**WITH DATA SORTED BY STATUS:**
After sorting by status: `[0,0,0,...,1,1,1,...,2,2,2,...]`.
RLE encoding: `(0, 70M), (1, 20M), (2, 10M)` → 12 bytes.
Then any codec achieves ~100,000:1 ratio on this column.
Total size: ~100 bytes. No codec needed — encoding did all the work.

**WITH COMPRESSION ON ENCODED COLUMN (sorted data):**
Real data rarely perfectly sorted. But even partially sorted:
RLE runs of 1000+ values of `0` → LZ4 achieves 100:1 ratio
easily. Snappy: 80:1. Even gzip adds little beyond encoding.

**THE INSIGHT:**
Encoding (dictionary, RLE, delta) and compression are
complementary. Encoding exploits domain-specific patterns
(repeated values, sequences). Compression exploits byte-level
patterns in the encoded output. The two stack: data that encodes
well also compresses well. This is why Parquet's columnar +
dictionary encoding + Snappy achieves 10× better results than
gzip alone on row-oriented text.

---

### 🧠 Mental Model / Analogy

> Think of compression as two stages of abbreviation. The first
> stage (encoding) uses domain knowledge: "I know there are only
> 3 possible status values, so I'll use a codebook (0=COMPLETE,
> 1=PENDING, 2=CANCELLED) and write numbers instead of text."
> The second stage (compression codec) uses byte-level pattern
> detection: "I see 70 million zeros in a row — I'll write
> '70M × zero' instead." Together they're a translator who
> first simplifies the vocabulary, then uses shorthand notation.

- "Domain knowledge codebook" → dictionary encoding
- "Shorthand notation" → LZ compression (back-references)
- "Translator's speed" → codec throughput
- "Shorthand efficiency" → compression ratio
- "Some words need more shorthand than others" → codec tuning

**Where this analogy breaks down:** Real compression works on
arbitrary bytes, not recognisable words. The LZ "shorthand"
works on any repeated byte sequence — it's content-agnostic.
The translator analogy suggests language understanding, but
compression is purely statistical.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Compression makes data smaller by finding patterns and storing
them more efficiently. Like a ZIP file for a document — the file
gets smaller but when you open it, it's exactly the same as the
original.

**Level 2 — How to use it (junior developer):**
In Parquet: `df.write.option("compression", "snappy").parquet(...)`.
Use Snappy as a default for Spark-to-Spark Parquet. Switch to
Zstd (level 3) for long-term storage where size matters. Never
use gzip for hot Parquet — it's too slow to compress in parallel.
For Kafka: `compression.type=snappy` for producers. For
REST/HTTP: `Content-Encoding: gzip` for API responses. Never
compress data that is already compressed (JPEG, MP3, already-
snappy Parquet) — re-compression adds CPU with no size gain.

**Level 3 — How it works (mid-level engineer):**
LZ4 uses a 16-byte hash chain with 64K window. Snappy uses 32-byte
blocks with 32K window. gzip uses 32K window with 3 hash chains.
Window size determines how far back to look for repetitions.
Larger window → better ratio → slower search. LZ4's tiny window
is why it's fast but misses long-distance repetitions that gzip
finds. Zstd uses a multi-level match-finder: a fast LZ77 front-end
for literal matching + a statistical back-end (ANS) for entropy
coding. ANS is strictly better than Huffman (gzip's entropy
coder) in theory and practice — it achieves near-theoretical
entropy limits at higher speed. Columnar Parquet: each column
chunk is independently compressed → parallel compression possible
→ 50-core Spark cluster compresses 50 column chunks simultaneously.

**Level 4 — Why it was designed this way (senior/staff):**
The Snappy paper (2011) and LZ4's design blog explicitly state
the same thesis: at Google/Facebook scale, the bottleneck is
I/O bandwidth (10 Gbps NICs, 500 MB/s disk), not CPU. Therefore
the correct trade-off is: accept 40% worse compression ratio
in exchange for 10× faster compression throughput, as long as
the compressed data still fits in I/O budget. The 2010s data
processing bottleneck was NIC (10 GbE) not CPU (multi-core 4 GHz).
By 2020, with 100 GbE NICs and NVMe SSDs at 7 GB/s, the balance
shifted: the CPU compressed data faster than storage could write
it. Zstd level 3 reflects this: the 2010s needed "as fast as
possible"; Zstd provides "as small as possible while staying
fast." For 2024 infrastructure, Zstd default level (3) is
the correct general choice — matching gzip ratio at Snappy speed.

---

### ⚙️ How It Works (Mechanism)

**LZ77 back-reference example:**
```
Input:  "the quick brown fox jumped over the quick"
         ^9 chars                    ^repeat at position 37

LZ output (simplified):
  "the quick brown fox jumped over " + <back-ref: pos=0, len=9>
  Result: 32 bytes literal + 3 bytes back-ref = 35 bytes
  vs 41 bytes raw = 15% saving for even this short string
```

**Parquet column compression pipeline:**
```
┌─────────────────────────────────────────────────────┐
│          PARQUET COLUMN COMPRESSION PIPELINE         │
│                                                      │
│  RAW COLUMN DATA                                     │
│  "COMPLETE","PENDING","COMPLETE","COMPLETE",...      │
│           ↓                                          │
│  DICTIONARY ENCODING                                 │
│  {0:"COMPLETE", 1:"PENDING", 2:"CANCELLED"}          │
│  [0, 1, 0, 0, 1, 2, 0, 0, 0, 1, ...]                │
│           ↓                                          │
│  RLE / BIT PACKING                                   │
│  2 bits per value (3 distinct → 2 bits sufficient)  │
│  [00,01,00,00,01,10,00,00,00,01,...]                 │
│           ↓                                          │
│  SNAPPY / ZSTD COMPRESSION                          │
│  Find byte-level runs and back-references            │
│  Compressed column chunk                             │
│           ↓                                          │
│  Stored in Parquet column chunk                      │
└─────────────────────────────────────────────────────┘

Typical result for a status-like column (3 distinct values,
100M rows):
  Raw text:    ~800 MB
  Dict-encoded: ~200 MB
  +RLE:         ~50 MB
  +Snappy:      ~20 MB     ← 40× compression vs raw text
```

---

### 💻 Code Example

**Example 1 — Benchmark compression codecs on a DataFrame:**
```python
import time, os
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
df = spark.read.parquet("s3://bucket/raw/")

for codec in ["none", "snappy", "gzip", "zstd", "lz4"]:
    path = f"/tmp/bench_{codec}"
    t0 = time.time()
    df.write.option("compression", codec) \
      .mode("overwrite").parquet(path)
    elapsed = time.time() - t0

    size = sum(
      f.stat().st_size for f in Path(path).rglob("*.parquet")
    )
    print(f"{codec:8s}: {size/1e9:.2f} GB in {elapsed:.1f}s")
```

**Example 2 — Kafka producer compression:**
```python
from confluent_kafka import Producer

# snappy: good general default
# lz4: best for < 1ms latency requirements
# gzip: best for network-constrained environments

producer = Producer({
    "bootstrap.servers": "broker:9092",
    "compression.type": "snappy",  # or "lz4", "zstd"
    "batch.size": 65536,           # larger batches = better ratio
    "linger.ms": 5,                # wait 5ms to fill batch
})
```

**Example 3 — HTTP gzip content encoding (Python):**
```python
import gzip, requests

# Server: compress response
import flask, gzip as gz

@app.route("/data")
def get_data():
    data = json.dumps(large_dict).encode()
    compressed = gz.compress(data)
    return flask.Response(
        compressed,
        headers={"Content-Encoding": "gzip",
                 "Content-Type": "application/json"}
    )

# Client: requests handles decompression automatically
r = requests.get("/data",
  headers={"Accept-Encoding": "gzip, deflate"})
data = r.json()  # auto-decompressed
```

---

### ⚖️ Comparison Table

| Codec | Comp. Speed | Decomp. Speed | Ratio | Splittable | Best For |
|---|---|---|---|---|---|
| **gzip** | Slow (50 MB/s) | Fast (250 MB/s) | ~3:1 | No (block-level) | Cold storage, HTTP APIs |
| **Snappy** | Fast (400 MB/s) | Fast (550 MB/s) | ~2:1 | No (block-level) | Hot Parquet, Kafka |
| **Zstd (L3)** | Fast (300 MB/s) | Fast (700 MB/s) | ~2.8:1 | No | General default (2024) |
| **LZ4** | Fastest (700 MB/s) | Fastest (3 GB/s) | ~1.5:1 | No | In-memory, real-time |
| **None** | N/A | N/A | 1:1 | Yes | Already-compressed data |

**How to choose:** Zstd (default level) for new data lake tables.
Snappy for real-time Kafka or existing Spark pipelines.
gzip for HTTP APIs and archival. LZ4 for in-memory columnar
databases (Redis, ClickHouse internal compression).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Higher compression ratio always means better performance | At standard pipeline scale, Snappy/Zstd outperform gzip because the I/O savings from slightly worse ratio are outweighed by faster write speed |
| Parquet files are always compressed | Parquet compression is configurable and defaults vary by tool. Spark default was `snappy`; some tools default to `none`. Always explicitly set compression |
| Compressing already-compressed data helps | LZ4 on a Snappy-compressed file typically adds 0–2% size improvement at full CPU cost. Never double-compress |
| Compression is only for storage | Kafka, HTTP, gRPC, inter-node Spark shuffle all benefit from compression — bandwidth is often the bottleneck, not CPU |
| gzip is splittable in Hadoop | gzip is NOT splittable — one gzip file = one MR mapper. Use Snappy or LZ4 for files you need to process in parallel. Parquet handles splitting at the row-group level regardless of codec |

---

### 🚨 Failure Modes & Diagnosis

**Non-Splittable gzip Causing Map-Only Spark Jobs**

**Symptom:**
Spark job on 50 gzip CSV files uses only 50 tasks despite 200
cores. CPU usage at 25%. Each task processes 10 GB.

**Root Cause:**
gzip is not splittable. Spark treats each gzip file as one
indivisible input split = one task. 200 cores cannot parallelise
within a single gzip file.

**Diagnostic Command / Tool:**
```bash
# Check file count vs task count
ls -la s3://bucket/data/*.csv.gz | wc -l
# If file count << executor count: split issue
```

**Fix:**
Convert gzip CSV to Parquet (Snappy). Parquet's row groups
are independently readable → 128 MB = 1 task regardless of
file count.

**Prevention:**
Never use gzip for bulk data files processed by Spark.
Only use gzip for HTTP APIs or per-file archival.

---

**Compression Type Mismatch Between Writer and Reader**

**Symptom:**
Spark reads a Parquet file and raises
`org.apache.parquet.io.ParquetDecodingException: codec not found:
BROTLI`.

**Root Cause:**
Writer used Brotli compression. Spark's Parquet library does not
include Brotli codec by default.

**Diagnostic Command / Tool:**
```python
import pyarrow.parquet as pq
meta = pq.read_metadata("file.parquet")
for i in range(meta.num_row_groups):
    for j in range(meta.row_group(i).num_columns):
        print(meta.row_group(i).column(j).compression)
# Shows compression per column chunk
```

**Fix:**
Re-write with a supported codec (Snappy or Zstd).

**Prevention:**
Standardise on one codec per organisation. Add codec to
data contract alongside schema version.

---

**CPU Bound on gzip for Streaming Kafka**

**Symptom:**
Kafka producer CPU usage at 95%. Throughput plateaued at 200K
msg/s despite having headroom. Switching to uncompressed
briefly increases throughput then degrades from I/O.

**Root Cause:**
gzip compression on Kafka producer is CPU-bound: each batch
compressed by one thread at 50 MB/s. At 200K × 1 KB messages/s
= 200 MB/s incoming, producer is bottlenecked on compression.

**Diagnostic Command / Tool:**
```bash
# JMX metrics on Kafka producer
kafka-producer-metrics.sh \
  --bootstrap-server broker:9092 --entity-name my-producer \
  | grep compression-rate
```

**Fix:**
Switch to Snappy or LZ4:
```python
producer_config["compression.type"] = "snappy"
# Compression rate drops from 3:1 to 2:1
# Compression throughput increases from 50 MB/s to 400 MB/s
```

**Prevention:**
Never use gzip on Kafka producers or Spark shuffle. Reserve
gzip for final cold storage writes where ratio > throughput.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Binary Formats` — compression is applied within binary
  format column chunks (Parquet, ORC) after type encoding
- `Columnar vs Row Storage` — columnar layout enables per-
  column compression which stacks multiplicatively with encoding
- `Data Types` — column type determines which encodings and
  compressions are most effective

**Builds On This (learn these next):**
- `Parquet` — Parquet applies per-column compression using
  these codecs; choosing the right codec affects Parquet
  read/write performance significantly
- `ORC` — ORC similarly applies per-stream compression within
  each stripe
- `Apache Kafka` — Kafka producer and broker compression
  settings directly use these codec names

**Alternatives / Comparisons:**
- `Serialization Formats` — compression is applied on top
  of serialisation; they are orthogonal concerns
- `Avro` — Avro files use these same codecs at the block level
  (separate from Kafka's message-level compression)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Lossless encoding that trades CPU time    │
│              │ for smaller byte representation           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Raw data bloats storage and network I/O   │
│ SOLVES       │ at a cost that exceeds compute savings    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The bottleneck is almost always I/O, not  │
│              │ CPU — faster compression → faster pipeline│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All data pipelines; all REST APIs; all    │
│              │ Kafka topics with significant payload size │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Already-compressed data (JPEGs, ZIPs,     │
│              │ already-snappy Parquet files)             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Compression ratio vs codec throughput     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Zstd: the codec that ended the           │
│              │  gzip-vs-Snappy debate."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Serialization Formats → Parquet →         │
│              │ Schema Registry                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A data team measures that their 100-core Spark cluster
writes 10 TB/day of Parquet with `compression=snappy`. The
Spark workers are CPU-idle 60% of the time. S3 costs are
$3,000/month for this data. An engineer proposes switching to
`compression=gzip`. Calculate the expected S3 cost reduction,
then estimate the write throughput impact, and explain whether
the trade-off is correct given the cluster's CPU idle state.
Then explain what would change if the cluster were CPU-bound at
95%.

**Q2.** A Kafka topic uses no compression. Messages are JSON,
average 2 KB each, 500K messages/second, 24 hours/day.
The topic retains 7 days. Calculate the total storage impact,
then compare the storage and network costs for Snappy, LZ4, and
Zstd at level 3. For each codec, explain the trade-off that
makes it the right or wrong choice for this specific scenario
(high-throughput, low-latency Kafka messaging).

