---
layout: default
title: "Master Data Management"
parent: "Data Fundamentals"
nav_order: 528
permalink: /data-fundamentals/master-data-management/
number: "0528"
category: Data Fundamentals
difficulty: ★★★
depends_on: Data Governance, Data Quality, Data Catalog, Data Lineage, Data Fabric
used_by: Data Governance, Data Quality, Data Catalog
related: Data Governance, Data Quality, Data Fabric, Data Catalog, Data Lineage
tags:
  - dataengineering
  - architecture
  - advanced
  - database
  - tradeoff
---

# 528 — Master Data Management

⚡ TL;DR — Master Data Management (MDM) creates and maintains a single, authoritative "golden record" for each core business entity — customer, product, supplier — across all systems.

| #528 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Data Governance, Data Quality, Data Catalog, Data Lineage, Data Fabric | |
| **Used by:** | Data Governance, Data Quality, Data Catalog | |
| **Related:** | Data Governance, Data Quality, Data Fabric, Data Catalog, Data Lineage | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A global retailer has 27 million customers. The CRM says "Apple Inc." (New York). The ERP says "Apple, Inc." (California). The billing system says "Apple Incorporated" (Delaware). The loyalty platform says "APPLE INC" with a different postal code. The customer service system shows Apple as four separate accounts — each with different order history. When the company offers Apple a custom enterprise contract, the account team cannot pull a single combined view of total spend. A cross-sell recommendation engine recommends products Apple already bought — on a different account. Revenue reports double-count Apple's spend. Duplicate marketing emails go to the same contacts from three CRM records.

**THE BREAKING POINT:**
In large organisations, the same real-world entity (customer, product, supplier, location) exists in dozens of source systems under different identifiers, spellings, and data models. There is no single truth. Every analytics query must guess which records belong to the same entity, producing inconsistent results across teams.

**THE INVENTION MOMENT:**
This is exactly why Master Data Management was created — a governed system that resolves all representations of the same entity into a single, trusted golden record, syndicated back to all consuming systems.

---

### 📘 Textbook Definition

**Master Data Management (MDM)** is a comprehensive method of enabling an enterprise to link all of its critical shared data — master data — to a single file called a master file or golden record. Master data refers to high-value, non-transactional entities that are shared across multiple systems: customers, products, suppliers, employees, locations, and accounts. An MDM system implements: **entity resolution** (identifying when two records from different systems refer to the same real-world entity), **data survivorship** (determining which attribute values to prefer when sources disagree), **golden record creation** (assembling the best attributes from all sources into a single authoritative record), and **syndication** (distributing the golden record back to consuming systems and maintaining synchronisation).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
MDM creates one official record for each customer, product, or supplier — combining all system versions into a single trusted truth.

**One analogy:**
> MDM is like a civil registry system for your data. When a person is born in different hospitals, files taxes in two states, and holds passports in two countries, different government systems hold conflicting records — different spellings, different dates, maybe even different ages. The civil registry creates a single canonical National ID record, verified and authoritative, that all government systems reference. Banks, hospitals, and agencies query the registry for the canonical version. MDM is the civil registry for your business entities.

**One insight:**
The hardest problem in MDM is not storage — it is **entity resolution** (also called record linkage or deduplication): determining algorithmically that "Apple Inc., NY" and "Apple Incorporated, DE" are the same company. This requires fuzzy matching (Levenshtein distance on names), probabilistic scoring (Fellegi-Sunter model), and often human review for uncertain matches. Getting entity resolution right is the difference between a useful MDM system and an expensive data problem.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The same real-world entity will always appear differently in different systems — this is unavoidable as systems are independently built.
2. There can only be one canonical truth about a real-world entity — MDM's job is to find and maintain it.
3. Source systems should not change — MDM reads from them but does not replace them; it resolves above them.

**DERIVED DESIGN:**

An MDM system has four stages:

**1. Ingestion:** Connect to all source systems. Extract master data entities (customer, product, etc.) with full attributes.

**2. Entity Resolution (Matching):**
- **Deterministic matching:** exact match on a trusted identifier (tax ID, ISIN, email) → certain same entity.
- **Probabilistic matching:** fuzzy name match + address proximity + phone match → confidence score. Records above threshold are linked; uncertain matches go to human review.

**3. Survivorship (Golden Record Assembly):**
Different sources have different data quality. Survivorship rules determine whose value "wins":
- `customer.email` → prefer CRM over ERP (CRM is more frequently updated)
- `customer.legal_name` → prefer government registry over internal system
- `customer.address` → prefer most recently verified address
The golden record is assembled from best-surviving attributes across all sources.

**4. Syndication:** The golden record is published back to consuming systems (warehouse, data lake, CRM) with the MDM-assigned global identifier (`master_customer_id`). All analytics and cross-system joins use this identifier.

**THE TRADE-OFFS:**
**Gain:** Single source of truth for business entities; accurate cross-system analytics; correct deduplication; regulatory compliance (AML/KYC, GDPR erasure).
**Cost:** MDM is a large investment — entity resolution accuracy requires extensive tuning; synchronisation with source systems adds latency; false matches (merging two different real-world entities) cause serious downstream damage; MDM systems themselves become a critical dependency.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce company has a customer in CRM (ID: C-9812, email: john.smith@example.com, address: 42 Baker St) and a customer in the ERP (ID: ERP-4491, email: j.smith@example.com, address: 42 Baker Street). Are they the same person?

**WHAT HAPPENS WITHOUT MDM:**
Analytics queries join CRM and ERP on email — they do not match (`john.smith@example.com ≠ j.smith@example.com`). The customer appears as two people. Their ERP order history is invisible to CRM-based analysis. A 360-degree customer view shows only half the purchase history. A personalisation engine recommends products they bought under the other ID. The duplicate is only discovered when John calls support.

**WHAT HAPPENS WITH MDM:**
The entity resolution engine computes: email similarity `john.smith` vs `j.smith` (same domain, partial name match) = 0.7; address similarity `42 Baker St` vs `42 Baker Street` (same number, same name, abbreviation) = 0.95; composite confidence score: 0.87. Above the threshold (0.80). The records are linked. MDM creates golden record `GR-00234`: `john.smith@example.com` (from CRM, more complete), `42 Baker St` (from CRM, verified delivery address), and assigns `master_customer_id = MASTER-0001`. Both source IDs are mapped to this master. All downstream analytics join on `master_customer_id`. John's complete purchase history is now visible.

**THE INSIGHT:**
Entity resolution is not a lookup — it is a probabilistic inference problem. The confidence threshold determines the false-positive/false-negative trade-off. Too low: you incorrectly merge two different people. Too high: you fail to link the same person under two spellings.

---

### 🧠 Mental Model / Analogy

> MDM is like a national postal addressing authority creating a canonical address standard. The same physical location might be written as "42 Baker St", "42 Baker Street", "42 BAKER ST, LONDON" and "Apartment 42, Baker Street" in different databases. The postal authority maintains the canonical form: "42 Baker Street, London, NW1 6XE" and maps all variants to it. Anyone needing the authoritative address uses the canonical mapping. MDM does this for all your business entities: customers, products, and suppliers.

**Mapping:**
- "Physical location" → real-world business entity (customer, product, supplier)
- "Address variant spellings" → same entity across multiple source systems
- "Postal authority canonical address" → MDM golden record
- "Postal code standardisation" → survivorship rules selecting the canonical attribute value
- "Postcode lookup API" → MDM identifier resolution API

**Where this analogy breaks down:** Addresses are geographically deterministic — two addresses are the same or not. MDM entity matching is probabilistic — there is always uncertainty in the confidence score, and human review is sometimes required.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Master Data Management is the process of making sure that when a company talks about "a customer named John Smith," every system is talking about the same John Smith — not six different database entries for slightly different versions of the same person.

**Level 2 — How to use it (junior developer):**
In a business with MDM implemented, all cross-system queries use `master_customer_id` instead of system-specific IDs. When building a pipeline that joins CRM to ERP, you join both through the MDM mapping table: `CRM.customer_id → MDM.master_id ← ERP.customer_id`. The MDM system publishes this mapping table and keeps it current. You never try to match CRM to ERP records directly.

**Level 3 — How it works (mid-level engineer):**
Probabilistic entity resolution uses Fellegi-Sunter model: compute `m` (probability of match given feature agreement) and `u` (probability of feature agreement by chance) across multiple comparison features (name, email, address, phone, date-of-birth). The likelihood ratio score `log(m/u)` is summed across features. Candidates above a threshold are auto-matched; candidates in a grey zone are queued for human review. Matched records are merged using survivorship rules (e.g., `COALESCE(most_recent_verified_email, any_email)`). Machine learning models (Spark MLlib, Dedupe.io) automate the weight estimation.

**Level 4 — Why it was designed this way (senior/staff):**
MDM was historically implemented as a "central hub" (all systems write through MDM before landing in their own system) or a "registry" (MDM maintains mappings; source systems are unchanged). Hub style gives stronger consistency but makes MDM a critical write path — an MDM outage blocks all transaction processing. Registry style is safer (source systems work without MDM) but creates eventual consistency delays. Cloud MDM platforms (Reltio, Stibo, Informatica MDM) now offer API-first, cloud-native approaches with ML-powered matching trained on each organisation's specific data patterns. The modern challenge: ML-based entity resolution models need retraining as entity distribution shifts — a model trained on North American name patterns performs poorly on Southeast Asian names. Bias in training data creates systematic match failures for underrepresented entity patterns.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│          MASTER DATA MANAGEMENT ARCHITECTURE             │
├──────────────────────────────────────────────────────────┤
│  SOURCE SYSTEMS                                          │
│  CRM (customer)  ERP (customer)  Billing (customer)     │
│       ↓                ↓                 ↓              │
├──────────────────────────────────────────────────────────┤
│  INGESTION                                               │
│  Extract all customer records → staging area            │
│  Standardise: format names, addresses, phone numbers    │
│  Normalise: "Baker St" → "Baker Street", "USA"→"US"     │
│                     ↓                                   │
├──────────────────────────────────────────────────────────┤
│  ENTITY RESOLUTION (MATCHING ENGINE)                    │
│  Blocking: partition candidates by name/email prefix    │
│    (avoids O(n²) comparisons on millions of records)    │
│  Comparison: compute similarity scores per field        │
│  Scoring: Fellegi-Sunter / ML model → confidence score  │
│  Decision:                                              │
│    score > 0.90 → auto-match                            │
│    0.70–0.90    → human review queue                    │
│    score < 0.70 → treat as distinct entities            │
│                     ↓                                   │
├──────────────────────────────────────────────────────────┤
│  SURVIVORSHIP → GOLDEN RECORD                           │
│  Apply rules: which source "wins" for each attribute    │
│  Assemble: one master record per entity                 │
│  Assign: global master_customer_id                      │
│  Track: source_id → master_id mapping for all sources  │
│                     ↓                                   │
├──────────────────────────────────────────────────────────┤
│  SYNDICATION                                             │
│  Publish golden records → Data Warehouse                │
│  Publish ID mapping → all consumer systems              │
│  API: GET /master/{id} → current golden record         │
│  Stream: delta changes → Kafka → downstream systems    │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Source systems → [MDM INGESTION ← YOU ARE HERE]
→ Entity resolution → Golden record creation → Syndication
→ Warehouse: master_customer_id in all fact tables
→ Downstream analytics: single truth per entity
```

**FAILURE PATH:**
```
Entity resolution false positive: two different customers merged
→ "Jane Smith NZ" and "Jane Smith AU" merged as same person
→ cross-sell recommendations and financial reports wrong
→ observable: business analyst notices customer with two addresses
   in different countries but same master record
→ MDM "un-merge" operation required + downstream correction
```

**WHAT CHANGES AT SCALE:**
At 100 million records, entity resolution using O(n²) pair comparison is infeasible. Blocking strategies (compare only records sharing the same first 3 letters of surname + same postal area code) reduce comparison space by 99.9%. At global scale (multi-language, multi-alphabet names), transliteration and Unicode normalisation are required before matching. The golden record syndication must use streaming (Kafka) rather than batch to keep consumer systems up-to-date within minutes.

---

### 💻 Code Example

Example 1 — Record standardisation:
```python
import re
import unicodedata

def standardise_name(name: str) -> str:
    """Normalise company name for MDM matching."""
    # Unicode normalise (handle accented characters)
    name = unicodedata.normalize("NFKD", name)
    # Uppercase
    name = name.upper()
    # Remove legal suffixes
    name = re.sub(
        r'\b(INC|INCORPORATED|LLC|LTD|LIMITED|CORP|CO)\b\.?',
        '', name
    )
    # Collapse whitespace
    return re.sub(r'\s+', ' ', name).strip()

print(standardise_name("Apple, Inc."))   # → "APPLE"
print(standardise_name("APPLE INCORPORATED"))  # → "APPLE"
```

Example 2 — Probabilistic matching (Dedupe.io):
```python
import dedupe

# Define fields for comparison
fields = [
    {"field": "name", "type": "String"},
    {"field": "email", "type": "String"},
    {"field": "address", "type": "Address"},
    {"field": "phone", "type": "Exact"}
]

# Train deduplicator (label some pairs as match/non-match)
deduplicator = dedupe.Dedupe(fields)
deduplicator.prepare_training(records)
dedupe.console_label(deduplicator)  # Human labels training examples
deduplicator.train()

# Cluster: identify which records are the same entity
threshold = 0.5
clustered_dupes = deduplicator.partition(records, threshold)

# clustered_dupes: list of clusters
# Each cluster = same real-world entity (golden record candidates)
for cluster_id, (records_in_cluster, scores) in \
    enumerate(clustered_dupes):
    print(f"Golden Record {cluster_id}: {records_in_cluster}")
```

Example 3 — Survivorship rule implementation:
```python
def apply_survivorship(cluster: list[dict]) -> dict:
    """Build golden record from cluster using survivorship rules."""
    # Sort by data source priority and recency
    cluster.sort(
        key=lambda r: (SOURCE_PRIORITY[r["source"]], r["updated_at"]),
        reverse=True
    )
    golden = {}
    # email: prefer CRM (source priority = 0) then most recent
    golden["email"] = next(
        (r["email"] for r in cluster if r.get("email")), None
    )
    # legal_name: prefer government registry
    golden["legal_name"] = next(
        (r["legal_name"] for r in cluster
         if r["source"] == "GOV_REGISTRY"), cluster[0]["legal_name"]
    )
    # address: prefer most recently verified
    cluster_with_address = [r for r in cluster if r.get("address")]
    golden["address"] = cluster_with_address[0]["address"] \
        if cluster_with_address else None
    return golden
```

---

### ⚖️ Comparison Table

| MDM Style | Source System Impact | Consistency | Availability Risk | Best For |
|---|---|---|---|---|
| **Registry (Virtual)** | None — no change | Eventual | Low | Large enterprises, cannot change sources |
| Hub (Physical) | Write through MDM | Strong | High (MDM becomes SPOF) | New greenfield builds |
| Consolidation | Batch pull, one-way | Batch-periodic | Low | Analytics-only golden record |
| Co-existence | Bidirectional sync | Near-real-time | Medium | Multi-system operational MDM |

**How to choose:** Use Registry style when source systems cannot be changed (most large-enterprise cases). Use Hub style only in greenfield projects where MDM can be engineered into the write path from day one. Consolidation is simplest and sufficient for analytics-only use cases.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| MDM replaces source systems | MDM reads from and writes back to source systems; it never replaces them — they remain the systems of record for transactions |
| Entity resolution is easy — just match on email | Email is the best single deterministic field but is often different across systems; probabilistic multi-field matching is required in practice |
| MDM is a one-time cleanup project | MDM is ongoing operational work — new records arrive daily, entities merge (company acquisitions), and golden records must be maintained continuously |
| A false match (incorrect merge) is easy to fix | Un-merging two incorrectly linked entities and correcting all downstream analytics is extremely expensive — false-positive matches must be prevented by tuning thresholds |
| MDM is only for customer data | MDM applies to any shared master entity: products, suppliers, employees, locations, financial accounts, and assets |

---

### 🚨 Failure Modes & Diagnosis

**False Positive Match (Incorrect Entity Merge)**

**Symptom:** Customer service agent reports a customer claiming they have orders they never placed — investigation reveals two different people matched as the same golden record.

**Root Cause:** Entity resolution threshold too low; two different people named "James Wilson" with similar postcodes were merged.

**Diagnostic Command / Tool:**
```sql
-- Find golden records with conflicting country presence
SELECT master_id, COUNT(DISTINCT country_code) AS country_count,
       COUNT(DISTINCT source_email) AS email_count
FROM mdm.entity_mapping
GROUP BY master_id
HAVING country_count > 1 OR email_count > 1;
-- Records with multiple countries/emails are merge candidates
```

**Fix:** Implement un-merge operation with full audit trail. Retune entity resolution threshold. Review: any golden record with source records from different countries requires human review.

**Prevention:** Set entity resolution threshold higher (0.92+) for high-risk entities. Require human review for any uncertain match above 0.75.

---

**Golden Record Drift (Sources Diverge)**

**Symptom:** The golden record for a customer shows old address; CRM was updated months ago and the golden record was never refreshed.

**Root Cause:** Syndication pipeline failed silently; the MDM golden record was not updated when the CRM record changed.

**Diagnostic Command / Tool:**
```sql
-- Find golden records older than their source records
SELECT m.master_id, m.last_updated AS golden_last_updated,
       s.updated_at AS source_last_updated
FROM mdm.golden_records m
JOIN mdm.entity_mapping em ON m.master_id = em.master_id
JOIN crm.customers s ON em.source_id = s.customer_id
WHERE s.updated_at > m.last_updated + INTERVAL '1 hour';
```

**Fix:** Monitor syndication pipeline health. Alert on golden records not updated within 2× their expected sync interval.

**Prevention:** Use event-driven synchronisation (Kafka change events from source → MDM update pipeline) rather than scheduled batch sync.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Data Quality` — entity resolution accuracy depends on standardised, quality input data
- `Data Governance` — MDM is the operational implementation of entity governance policies

**Builds On This (learn these next):**
- `Data Fabric` — uses MDM golden records as the canonical entity reference for federated integration
- `Data Catalog` — surfaces the MDM golden record as the authoritative entity definition

**Alternatives / Comparisons:**
- `Entity Resolution (standalone)` — probabilistic record linkage without the full MDM governance wrapper
- `Reference Data Management` — manages controlled vocabulary lists (country codes, currency codes) — simpler subset of MDM

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ System creating one authoritative        │
│              │ "golden record" per entity across systems│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Same customer/product in 10 systems with │
│ SOLVES       │ different IDs → broken analytics         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Entity resolution is probabilistic —     │
│              │ threshold choice determines false-match  │
│              │ vs false-split trade-off                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Same entity in 3+ source systems with    │
│              │ inconsistent identifiers or spelling     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple single-source systems or start-ups│
│              │ — overhead exceeds benefit               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Single truth + analytics accuracy vs     │
│              │ large implementation cost + merge risk   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The civil registry for your data —      │
│              │  one canonical ID for every real entity" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Governance → Data Fabric →          │
│              │ Data Catalog                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your MDM entity resolution model is running at 96.5% precision (3.5% false positive merge rate) on 50 million customer records. That means approximately 1.75 million customers are incorrectly merged with someone else. Each incorrect merge takes a data steward 15 minutes to investigate and un-merge. Calculate the operational cost of this precision level. What precision threshold would be economically justifiable, and what is the trade-off you accept when you raise the threshold (lower false positives but higher false negatives)?

**Q2.** A company acquires a competitor with 8 million customer records. The acquired company used integer IDs, stored names in a single `full_name` field, recorded addresses only in Chinese characters, and had no email field. Your MDM system was trained on Western European name/address patterns. How do you approach entity resolution for this acquisition? What preprocessing steps are required, what new training data do you need, and how do you measure whether the resulting golden records are accurate before syndicating them to all consuming systems?

