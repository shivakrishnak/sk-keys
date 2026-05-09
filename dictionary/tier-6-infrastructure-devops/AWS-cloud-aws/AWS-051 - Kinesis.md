---
version: 1
layout: default
title: "Kinesis"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 51
permalink: /cloud-aws/kinesis/
id: AWS-051
category: "Cloud - AWS"
difficulty: "★★★"
depends_on:
  ["AWS Global Infrastructure", "IAM (Identity and Access Management)"]
used_by: ["CloudWatch", "AWS Cost Optimization"]
related: ["SQS", "SNS", "DynamoDB", "Lambda", "CloudWatch"]
tags: [aws, kinesis, streaming, data-stream, firehose, real-time, cloud]
---

# Kinesis

## ⚡ TL;DR

**Kinesis** is AWS's real-time data streaming platform. **Kinesis Data Streams** (KDS): ordered, replayable, sharded event stream - multiple independent consumers, data retained 24hr-365 days. **Kinesis Data Firehose**: load streaming data into S3/Redshift/OpenSearch without coding. **Kinesis Data Analytics**: run SQL/Flink on streams. Key differentiator vs SQS: replay, ordered per shard, multiple independent consumers reading same stream.

---

## 🔥 Problem This Solves

SQS: message consumed and deleted; no replay; consumers compete for messages. For clickstream, IoT, real-time analytics, fraud detection: you need ordered events, replay capability, and multiple independent processors (analytics service AND fraud detection BOTH reading the same stream). Kinesis provides this.

---

## 📘 Textbook Definition

Amazon Kinesis Data Streams is a scalable and durable real-time data streaming service. Producers put records into named shards; consumers read from shards using sequence numbers. Records are retained 24 hours (default) to 365 days. Multiple consumer applications can read the same stream independently. Records within a shard are strictly ordered.

---

## ⏱️ 30 Seconds

```
Kinesis Data Streams:
  Shard: basic unit of capacity
    Write: 1 MB/s or 1000 records/s per shard
    Read:  2 MB/s per shard (shared across consumers)
  Partition key: determines which shard receives record
  Sequence number: ordering within shard
  Retention: 24hr default, up to 365 days ($)

Enhanced Fan-out:
  2 MB/s PER consumer (vs shared 2MB/s)
  Push-based (lower latency)
  Additional cost: $0.015/shard-hour + $0.013/GB

Kinesis Firehose:
  Managed delivery: Kinesis → S3/Redshift/OpenSearch
  No consumers to manage
  Buffering: up to 900s or 128MB
  Transformations via Lambda
```

---

## 🔩 First Principles

- **Shard = ordered lane**: all records with same partition key go to same shard → ordered per partition key
- **Hot shards**: high-cardinality partition keys distribute load; low-cardinality = hot shard = throttling
- **Consumer checkpoint**: consumers track position via sequence number + DynamoDB; resume from last checkpoint on restart
- **GetRecords vs Enhanced Fan-out**: GetRecords = polling, shared 2MB/s per shard; Enhanced Fan-out = push, 2MB/s per registered consumer
- **KCL (Kinesis Client Library)**: manages shard assignment, checkpointing, retries automatically

---

## 🧪 Thought Experiment

E-commerce platform: clickstream data (100K events/sec). Need: (1) real-time fraud detection, (2) analytics dashboard, (3) user journey analysis, (4) nightly S3 export. With Kinesis: all 4 consumers read the SAME stream independently. Fraud detection at sub-second (Enhanced Fan-out). Analytics at 5-second intervals. User journey app at its own pace. Firehose dumps to S3 hourly. Add consumer #5 anytime without changing producers.

---

## 🧠 Mental Model / Analogy

Kinesis is like a **highway with multiple lanes (shards)**. Cars (records) drive on lanes determined by their license plate (partition key). Multiple toll booth operators (consumers) independently monitor the entire highway - each sees all cars from their own vantage point and keeps track of which cars they've already logged. Unlike SQS (cars drive past a single toll booth and are done), highway cars stay visible for 24 hours so any late-arriving inspector can review them.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Put records with partition key. Consumer reads records from shard(s). Records retained 24 hours. Multiple apps can read same stream.

**Level 2 - Practitioner**: KCL for Java: manages shard discovery, checkpointing, and lease management automatically. Firehose: buffer clickstream data to S3 as Parquet for Athena queries. Shard sizing: 1 shard per 1MB/s write; add shards via resharding (split/merge, no downtime).

**Level 3 - Advanced**: Enhanced Fan-out: register consumer for dedicated 2MB/s per shard (reduces latency from ~200ms polling to ~70ms push). Lambda as Kinesis consumer: event source mapping, parallel processing per shard. Kinesis Aggregation: batch multiple small records into one Kinesis record (up to 1MB) using KPL for throughput efficiency.

**Level 4 - Expert**: Kinesis Data Analytics / Apache Flink: stateful stream processing (windowed aggregations, joins, complex event patterns). KEDA + Kinesis: auto-scale K8s consumers based on shard iterator age (lag). Kinesis vs Kafka: Kinesis managed but less flexible (max 365 days, fixed shard-based throughput, $0.015/shard-hr); Kafka on MSK = more control, potentially cheaper at large scale, supports more consumer patterns. Hot shard mitigation: add random salt to partition key (`userId + random(0,100)`) to distribute across shards, then deduplication downstream. KPL (Kinesis Producer Library): retry, aggregation, async puts; KCL on consumer side: checkpoint to DynamoDB, balanced shard assignment.

---

## ⚙️ How It Works

### Kinesis Data Streams (Terraform)

```hcl
resource "aws_kinesis_stream" "events" {
  name             = "application-events"
  shard_count      = 10        # 10 MB/s write, 20 MB/s read

  retention_period = 168       # 7 days (hours)

  # Server-side encryption
  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.kinesis.arn

  # Enhanced monitoring
  shard_level_metrics = [
    "IncomingBytes",
    "OutgoingBytes",
    "OutgoingRecords",
    "ReadProvisionedThroughputExceeded",
    "WriteProvisionedThroughputExceeded",
    "IteratorAgeMilliseconds"
  ]

  tags = {
    Environment = "prod"
  }
}

# Enhanced Fan-out consumer
resource "aws_kinesis_stream_consumer" "fraud_detector" {
  name       = "fraud-detector"
  stream_arn = aws_kinesis_stream.events.arn
}
```

### Kinesis Producer (Java Spring Boot)

```java
@Service
public class ClickstreamProducer {

    private final KinesisClient kinesisClient;

    @Value("${aws.kinesis.stream-name}")
    private String streamName;

    // Single record put
    public void publishEvent(ClickEvent event) {
        String payload = JsonUtils.serialize(event);

        kinesisClient.putRecord(PutRecordRequest.builder()
            .streamName(streamName)
            .partitionKey(event.getUserId())  // same user = same shard = ordered
            .data(SdkBytes.fromUtf8String(payload))
            .build());
    }

    // Batch put (more efficient)
    public void publishEvents(List<ClickEvent> events) {
        List<PutRecordsRequestEntry> entries = events.stream()
            .map(event -> PutRecordsRequestEntry.builder()
                .partitionKey(event.getUserId())
                .data(SdkBytes.fromUtf8String(JsonUtils.serialize(event)))
                .build())
            .collect(Collectors.toList());

        PutRecordsResponse response = kinesisClient.putRecords(
            PutRecordsRequest.builder()
                .streamName(streamName)
                .records(entries)
                .build()
        );

        // Handle partial failures
        if (response.failedRecordCount() > 0) {
            List<PutRecordsResultEntry> failed = response.records().stream()
                .filter(r -> r.errorCode() != null)
                .collect(Collectors.toList());
            log.warn("Failed to publish {} records", failed.size());
            // Retry failed records
        }
    }
}
```

### KCL Consumer (Java)

```java
// IRecordProcessor implementation for KCL v2
public class ClickEventProcessor implements ShardRecordProcessor {

    private String shardId;

    @Override
    public void initialize(InitializationInput initializationInput) {
        this.shardId = initializationInput.shardId();
        log.info("Initialized processor for shard {}", shardId);
    }

    @Override
    public void processRecords(ProcessRecordsInput processRecordsInput) {
        List<KinesisClientRecord> records = processRecordsInput.records();

        for (KinesisClientRecord record : records) {
            try {
                String payload = StandardCharsets.UTF_8.decode(record.data()).toString();
                ClickEvent event = JsonUtils.deserialize(payload, ClickEvent.class);
                processEvent(event);
            } catch (Exception e) {
                log.error("Error processing record {}: {}", record.sequenceNumber(), e);
                // Don't checkpoint; record will be retried
            }
        }

        // Checkpoint: marks all records up to last as processed
        // Stored in DynamoDB by KCL
        try {
            processRecordsInput.checkpointer().checkpoint();
        } catch (Exception e) {
            log.error("Checkpoint failed for shard {}", shardId, e);
        }
    }
}
```

### Kinesis Firehose (Terraform)

```hcl
resource "aws_kinesis_firehose_delivery_stream" "events_to_s3" {
  name        = "events-to-s3"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.events.arn
    prefix     = "events/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"

    # Buffer settings
    buffering_size     = 128  # MB
    buffering_interval = 300  # seconds

    # Convert to Parquet (efficient for Athena)
    data_format_conversion_configuration {
      output_format_configuration {
        serializer {
          parquet_ser_de {}
        }
      }
      input_format_configuration {
        deserializer {
          open_x_json_ser_de {}
        }
      }
      schema_configuration {
        database_name = aws_glue_catalog_database.events.name
        table_name    = aws_glue_catalog_table.click_events.name
        role_arn      = aws_iam_role.firehose.arn
      }
    }
  }
}
```

---

## ⚖️ Comparison Table: Kinesis vs Kafka (MSK) vs SQS

|                | Kinesis Data Streams   | MSK (Kafka)                    | SQS                 |
| -------------- | ---------------------- | ------------------------------ | ------------------- |
| **Ordering**   | Per shard              | Per partition                  | FIFO option         |
| **Replay**     | ✅ (1-365 days)        | ✅ (configurable)              | ❌                  |
| **Fan-out**    | Multiple consumers     | Multiple consumers             | Competing consumers |
| **Management** | Fully managed          | Managed (broker config needed) | Fully managed       |
| **Cost**       | $0.015/shard-hr + data | EC2 + storage                  | $0.40/million msgs  |
| **Scale**      | Shard-based            | Partition-based                | Automatic           |
| **Use case**   | AWS-native streaming   | Complex Kafka ecosystems       | Simple queuing      |

---

## ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                                               |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| "More shards = always better"       | Too many shards increase cost; size to write throughput + consumer read demand                                        |
| "Kinesis = SQS with ordering"       | Fundamentally different: Kinesis supports replay, multiple independent consumers, and ordered streams; SQS is a queue |
| "Enhanced Fan-out is always needed" | Standard GetRecords (polling) is fine for non-latency-sensitive; Enhanced Fan-out for <70ms requirements              |
| "Partition key doesn't matter"      | Hot shards from low-cardinality partition keys cause throttling; design for uniform distribution                      |

---

## 🔗 Related Keywords

- [SQS](/cloud-aws/sqs/) - simpler queue when ordering and replay not needed
- [SNS](/cloud-aws/sns/) - fan-out to multiple subscribers
- [Lambda](/cloud-aws/lambda/) - serverless Kinesis consumer

---

## 📌 Quick Reference Card

```bash
# List streams
aws kinesis list-streams

# Put record
aws kinesis put-record \
  --stream-name my-stream \
  --partition-key user-123 \
  --data "$(echo '{"event":"click"}' | base64)"

# Get shard iterator
SHARD_ID=$(aws kinesis describe-stream \
  --stream-name my-stream \
  --query 'StreamDescription.Shards[0].ShardId' --output text)

ITERATOR=$(aws kinesis get-shard-iterator \
  --stream-name my-stream \
  --shard-id $SHARD_ID \
  --shard-iterator-type TRIM_HORIZON \
  --query ShardIterator --output text)

# Read records
aws kinesis get-records --shard-iterator $ITERATOR

# Check iterator age (consumer lag)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Kinesis \
  --metric-name GetRecords.IteratorAgeMilliseconds \
  --dimensions Name=StreamName,Value=my-stream \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period 60 --statistics Maximum
```

---

## 🧠 Think About This

The most important Kinesis operational metric is `GetRecords.IteratorAgeMilliseconds` (iterator age). This measures how far behind your consumer is from the latest records in the stream - essentially consumer lag. If iterator age is growing, your consumer cannot keep up with the producer throughput and is falling behind. Near-zero: healthy, processing in real-time. Growing rapidly: under-scaled, scale up consumers or add shards. Alert at: >5 minutes for real-time systems, >1 hour for batch systems. Alert at 60% of retention period (if retention=24hr and lag=14hr, you'll lose events before processing them). This single metric tells you everything about the health of your Kinesis pipeline.
