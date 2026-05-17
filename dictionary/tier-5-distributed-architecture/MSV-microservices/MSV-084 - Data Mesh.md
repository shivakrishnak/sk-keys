---
id: MSV-084
title: Data Mesh
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-001, MSV-003, MSV-080, MSV-081
used_by: MSV-001
related: MSV-001, MSV-003, MSV-080, MSV-081, MSV-082, MSV-042
tags:
  - microservices
  - dataengineering
  - deep-dive
  - architecture
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 84
permalink: /microservices/data-mesh/
---

# MSV-084 - Data Mesh

⚡ TL;DR - Data Mesh (Zhamak Dehghani, 2019):
decentralized data architecture applying
microservices principles to analytical data.
Four principles: (1) Domain ownership of data
(teams own their data end-to-end, including
analytical data). (2) Data as a product (data
sets are treated as products with owners, SLOs,
and quality guarantees). (3) Self-serve data
infrastructure (platform team provides tools
so domain teams can publish/consume data
without central data engineering team). (4)
Federated computational governance (policies
are federated; central governance sets standards,
not centrally executes everything). Context:
challenges the centralized data warehouse/data
lake model. Reality check: Data Mesh is an
organizational and architectural strategy, not
a technology. Very difficult to implement.

| #084 | Category: Microservices | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | What are Microservices, Domain-Driven Design, Conway's Law in Microservices, Team Topologies | |
| **Used by:** | What are Microservices | |
| **Related:** | What are Microservices, Domain-Driven Design, Conway's Law in Microservices, Team Topologies, Service Ownership Model, Eventual Consistency | |

---

### 🔥 The Problem This Solves

**CENTRALIZED DATA WAREHOUSE BOTTLENECK:**
Large org: 20 microservices, each owning its
DB. Central data engineering team: 8 people,
responsible for data warehouse and analytics.
50 data requests from product teams: waiting
in the queue. Average time to new analytics
report: 6 weeks (requirement -> ticket ->
 data engineer build pipeline -> validate ->
publish). The payment team: wants analytics
on payment failure rates. Queue: 2 months
out. Finance team: uses 3-month-old data.
Marketing team: still waiting for Q2 funnel
data in Q3. Data engineering team: burned
out. Data: strategic bottleneck. Data Mesh:
shift data ownership to domain teams; central
data team: provides infrastructure, not pipelines.

---

### 📘 Textbook Definition

**Data Mesh** is a decentralized sociotechnical
architecture (Zhamak Dehghani, ThoughtWorks,
2019) for managing analytical data at scale
using four principles:

**Principle 1: Domain Ownership of Data**
Domain teams: own their analytical data, not
just their operational DB. Payment Team:
owns and publishes `payments-domain-data`
(not just the payments DB). The domain team:
responsible for data quality, freshness,
schema, and SLOs for their data products.
Central data engineering team: no longer
responsible for building pipelines for every
domain.

**Principle 2: Data as a Product**
Data sets are treated as products:
- Discoverable: listed in a data catalog
- Addressable: stable access URL/API
- Trustworthy: data quality SLOs (freshness,
  completeness, accuracy)
- Self-describing: schema documented
- Interoperable: standard formats
  (Apache Parquet, Avro, Delta Lake)
- Secure: access control per consumer

**Principle 3: Self-Serve Data Infrastructure**
Platform team (data platform): provides tools
that allow domain teams to publish data products
without needing specialized data engineering
knowledge. Example: templated data pipelines,
automated schema registration, self-service
data catalog registration.

**Principle 4: Federated Computational Governance**
Global policies (data residency, PII handling,
retention): defined centrally but EXECUTED
by each domain team in their data product.
Domain teams: autonomous within governance
boundaries. Not "central team enforces everything"
but "central team sets rules; domain teams
comply and prove it".

**Data Mesh vs Data Lake/Data Warehouse:**
- Data Lake: central repository, all raw data.
  Central team: manages schema, quality.
  Problem: swamp (poor quality, undiscoverable).
- Data Warehouse: curated, modeled centrally.
  Problem: central team bottleneck, slow.
- Data Mesh: distributed ownership; each domain:
  publishes data products. Central: governance
  + infrastructure platform only.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Data Mesh: microservices principles applied
to data. Domain teams own their data. Data
treated as a product. Central team: provides
platform, not pipelines.

**One analogy:**
> Data Mesh is like moving from a central
> government that manages everything to a
> federal system. Old model: all data flows
> to the central capital (data warehouse) where
> central administrators (data engineers) process
> and distribute it. Data Mesh: states (domains)
> manage their own data (like states manage
> their own affairs). Federal government
> (data platform): sets standards and provides
> infrastructure (roads, laws). States: autonomous
> within federal standards. Travelers (analysts):
> can visit any state (data product) using
> a consistent travel system (catalog + standards).

**One insight:**
Data Mesh is primarily an organizational change,
not a technology change. The technology (Parquet,
Delta Lake, data catalog, data platform) exists
today. The HARD part: getting domain teams
to accept responsibility for analytical data
quality and schema stability. Domain teams:
accustomed to only owning their operational
DB. Now they must: publish data products,
maintain schema backward compatibility,
monitor data freshness SLOs, and respond to
consumer questions. This is the same "you
build it, you run it" shift that microservices
required - but for data.

---

### 🔩 First Principles Explanation

**DATA MESH ARCHITECTURE IN PRACTICE:**

```
TRADITIONAL CENTRALIZED MODEL:

  Payment DB --> [Central ETL Pipeline]
  Order DB   --> [Central ETL Pipeline] --> Data Warehouse
  User DB    --> [Central ETL Pipeline]
  Catalog DB --> [Central ETL Pipeline]

  Central Data Engineering Team:
    Builds + maintains all ETL pipelines
    Manages Data Warehouse schema
    Responds to all analytics requests
    BOTTLENECK: all data flows through one team

DATA MESH MODEL:

  Payment Team:
    Payment DB
    Payment Data Product Pipeline (owns)
    Publishes: payments-domain/v1
      (Parquet files in S3/Delta Lake)
      Schema: payment_id, amount, status,
              timestamp, customer_id
      SLO: 99.5% freshness < 1 hour
      Owner: Payment Team
      Catalog: registered in data catalog

  Order Team:
    Order DB
    Order Data Product Pipeline (owns)
    Publishes: orders-domain/v1
      SLO: 99.5% freshness < 30 minutes

  Data Platform Team (provides):
    Data catalog (discovery)
    Pipeline templates (Airflow/dbt templates)
    Schema registry (Confluent/AWS Glue)
    Access control infrastructure
    Data quality framework (Great Expectations)
    Storage infrastructure (S3, Delta Lake)

  Consumers (Data Analysts, ML Teams):
    Discover data in catalog
    Access payments-domain/v1 directly
    No ticket to central team needed
    SLO: guaranteed freshness and quality
```

**DATA PRODUCT DEFINITION:**

```yaml
# Data product specification (example)
apiVersion: data-mesh/v1
kind: DataProduct
metadata:
  name: payments-domain
  version: v1
  owner: payment-team
spec:
  description: All payment transactions
    from the payments microservice
  domain: payments
  
  output:
    type: delta-lake-table
    location: s3://data-mesh/payments/v1/
    format: delta
    schema_registry: glue://payments/transactions/v1
    
  slo:
    freshness: 60min  # data not older than 60min
    completeness: 99.9%  # all transactions present
    accuracy: 99.99%  # amounts match source
    
  governance:
    pii_fields: [customer_id, card_last_4]
    pii_handling: masked  # not raw PII in product
    retention: 7years
    access_control: rbac  # row-level security
    
  consumers:
    - finance-team: read-access
    - fraud-team: read-access
    - ml-team: read-access
```

---

### 🧪 Thought Experiment

**REAL DATA MESH FAILURE: TOO MANY MOVING PARTS**

```
Common Data Mesh failure pattern:

  Company: 15 domain teams
  Goal: implement Data Mesh
  Year 1 effort:
    - Data catalog: purchased (Alation)
    - Data platform: built (Airflow + S3 + Glue)
    - Training: all 15 teams on dbt + Airflow
    - Governance committee: formed
    
  Year 1 reality:
    - 3 of 15 teams: published data products
      (the 3 teams that had data-savvy engineers)
    - 12 of 15 teams: stuck
      (no data engineering skill in team)
      (platform: too complex to self-serve)
    - Data catalog: 40% of products registered
    - Data quality SLOs: not monitored by domains
    - Consumers: can find data but quality unknown
    - Central data team: still doing ETL for
      12 teams (shadow pipeline team)
    
  Root cause:
    Self-serve platform: not self-serve enough
    Domain teams: lacked data skills
    Platform team: didn't invest in golden path
    Governance: committee overhead, no tooling
    
  Lesson:
    Data Mesh requires:
    (1) PLATFORM: genuinely self-serve (not just
        documented, but automated golden path)
    (2) SKILLS: domain teams need some data literacy
        (enabling team for 6 months minimum)
    (3) GOVERNANCE: automated (policy as code,
        not committee meetings)
    Start small: 2-3 willing domains; prove value;
    then expand. Don't mandate all 15 at once.
```

---

### 🧠 Mental Model / Analogy

> Data Mesh is like the shift from traditional
> publishing to social media. Old publishing:
> content creators submit to publishers (central
> data engineering team) who edit, format, and
> distribute (data warehouse). Publishers:
> bottleneck. Data Mesh: each creator publishes
> directly on their platform (domain team publishes
> data product). Platform (Twitter/Substack =
> data platform): provides the infrastructure
> (publishing tools, discovery, access control).
> Community standards (data governance): apply
> to all creators. Quality: varies; consumers:
> must check quality signals (SLOs, endorsements).
> Some creators: excellent. Others: poor quality
> (same with domain data products). Central
> publisher: no longer the gatekeeper.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Data Mesh: instead of one central team owning
all data pipelines, each product team owns
its own data. The team: publishes their data
in a standard format that others can use.

**Level 2 - Data product basics (junior developer):**
A data product: a dataset published by a domain
team with a guaranteed schema, freshness SLO,
and quality guarantee. Example: Payment Team
publishes `payments_transactions_v1` as a Delta
Lake table in S3, updated every 30 minutes,
99.9% completeness guaranteed. Any analyst:
can query it directly without asking the
Payment Team.

**Level 3 - dbt + domain ownership (mid-level):**
dbt (data build tool): the standard for domain
teams to define their data transformations.
Payment Team: writes dbt models that transform
raw `payments` DB tables into the clean
`payments_transactions_v1` data product.
dbt: handles schema documentation, lineage,
testing (data quality assertions). Platform
team: runs dbt in Airflow (or dbt Cloud).
Domain team: defines transformations; platform:
orchestrates.

**Level 4 - Federated governance (senior):**
Federated governance: central team defines
policies ("no PII in data products without
masking"); domain teams implement policies
in their data product pipelines (mask customer
IDs before publishing). Automated enforcement:
great expectations data quality checks run
in CI/CD before publishing. Data contract:
if downstream consumer breaks on schema
change, domain team must version the product
(`v1` -> `v2`) and maintain `v1` for migration
period. Federated governance: balances autonomy
and standardization.

**Level 5 - Data Mesh organizational prerequisites (principal):**
Data Mesh is NOT for every organization. Prerequisites:
(1) Multiple autonomous domain teams with
data-literate engineers (or enabling investment);
(2) Scale where central data team is a demonstrated
bottleneck (usually > 20 domain teams, or
> 100 data consumers); (3) Leadership commitment
to domain teams taking on data ownership
responsibility (not just the data platform);
(4) Platform team investment in genuine self-serve
tools (not just documentation). Warning signs
not to adopt Data Mesh: < 10 domain teams
(central model is fine), no platform team
capacity to build IDP for data, domain teams
not willing to own data quality.

---

### ⚙️ How It Works (Mechanism)

```python
# Domain team's dbt model (Payment Team)
# Defines the payments data product
# dbt: handles SQL transformation + testing

# models/payments/payments_transactions_v1.sql:
WITH source AS (
    -- Raw data from operational payments DB
    -- (via CDC / event stream to data lake)
    SELECT * FROM raw.payments.transactions
    WHERE _synced_at >= CURRENT_TIMESTAMP - INTERVAL 2 HOURS
),
cleaned AS (
    SELECT
        payment_id,
        order_id,
        -- Mask PII per governance policy
        SHA2(customer_id, 256) AS customer_id_hash,
        amount_cents / 100.0 AS amount_usd,
        currency,
        status,  -- 'succeeded', 'failed', 'refunded'
        payment_method_type,
        failure_code,
        created_at,
        updated_at
    FROM source
    WHERE payment_id IS NOT NULL  -- basic quality
)
SELECT * FROM cleaned

-- tests/payments_transactions_v1.yml:
-- models:
--   - name: payments_transactions_v1
--     tests:
--       - unique: payment_id
--       - not_null: [payment_id, amount_usd, status]
--       - accepted_values:
--           column_name: status
--           values: [succeeded, failed, refunded]
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
DATA MESH END-TO-END:

  OPERATIONAL LAYER:
    Payment microservice
      -> payments PostgreSQL DB
      -> CDC (Debezium) -> Kafka

  INGESTION LAYER (Platform provides):
    Kafka -> S3 raw zone (every 5 minutes)
    Raw zone: append-only, original format

  TRANSFORMATION LAYER (Domain team owns):
    Airflow DAG (Payment Team's dbt job)
    -> reads from S3 raw zone
    -> runs dbt transformations
    -> data quality tests (Great Expectations)
    -> publishes to Delta Lake: payments/v1/

  DATA PRODUCT LAYER:
    payments-domain/v1:
      Location: s3://data-mesh/payments/v1/
      Freshness SLO: updated < 1 hour
      Schema: documented in Glue catalog
      Quality: 99.9% completeness assured

  DISCOVERY LAYER (Platform provides):
    Data catalog (Alation/DataHub)
    -> Payment Team registers payments/v1
    -> Consumers discover and request access

  CONSUMPTION LAYER:
    Finance analysts: Redshift Spectrum
    ML team: PySpark on EMR
    BI team: Tableau -> Redshift
    All read payments/v1 directly
    No central data engineering team involved
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Centralized ETL vs Domain-owned data product**

```python
# BAD: Domain team asks central data engineering
# team to build an ETL pipeline
# Ticket submitted by Payment Team:
# "Please build pipeline for payment failure analysis"
# Status: in queue (2 months backlog)
# Central team: builds pipeline 8 weeks later
# Payment Team: owns operational DB but NOT
# their analytical data
# Result: Payment Team waits 2 months for
# insights about their own service

# central_team_pipeline.py (bottleneck model):
def build_payment_pipeline():
    # Central data engineer: unfamiliar with
    # payment domain semantics
    # "what does failure_code=204 mean?"
    # Must ask Payment Team -> delays
    pass  # 8 weeks of ticket hell
```

```python
# GOOD: Payment Team owns their data product
# dbt model + Airflow DAG owned by Payment Team
# Platform team: provides Airflow + S3 + dbt
# infra but NOT the pipelines

# payments/models/payment_failure_analysis.sql
# Owned by: Payment Team
# Payment Team: knows the domain semantics
# No ticket to central team needed

WITH failures AS (
    SELECT
        DATE_TRUNC('hour', created_at) AS hour,
        failure_code,
        payment_method_type,
        COUNT(*) AS failure_count,
        AVG(amount_usd) AS avg_failed_amount
    FROM {{ ref('payments_transactions_v1') }}
    WHERE status = 'failed'
    AND created_at >= CURRENT_TIMESTAMP
        - INTERVAL 30 DAYS
    GROUP BY 1, 2, 3
)
SELECT
    hour,
    failure_code,
    payment_method_type,
    failure_count,
    avg_failed_amount,
    -- Payment team knows: code 204 = bank decline
    CASE failure_code
        WHEN '204' THEN 'bank_decline'
        WHEN '402' THEN 'insufficient_funds'
        WHEN '501' THEN 'fraud_suspected'
        ELSE 'other'
    END AS failure_reason
FROM failures

-- Time to insight: 1 day (Payment Team builds it)
-- vs 8 weeks (central team ticket)
-- Quality: better (Payment Team knows the domain)
```

---

### ⚖️ Comparison Table

| Approach | Data Ownership | Scalability | Query Freshness | Skill Required |
|---|---|---|---|---|
| **Data Warehouse (central)** | Central data team | Poor (team bottleneck) | Hours/days | Central data engineers |
| **Data Lake (central)** | Central data team | Better (storage scale) | Variable | Central data engineers |
| **Data Mesh** | Domain teams | High (distributed ownership) | Per SLO | Domain teams need data skills |
| **Data Lakehouse** | Mixed | High (Delta Lake scale) | Minutes | Mixed team skills |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Data Mesh is a technology architecture (replace data warehouse with specific tools) | Data Mesh is an organizational + architectural strategy, not a tool. Dehghani explicitly: "data mesh is not about technology." The same tools (Delta Lake, dbt, Kafka, S3) can be used in a centralized or Data Mesh model. The difference: WHO owns the data pipelines and data quality. Technology change without organizational change = centralized model with new tools. |
| Data Mesh means domain teams become mini data engineering teams | Data Mesh: domain teams become responsible for their data PRODUCTS (outputs), not for data INFRASTRUCTURE. The platform team (data platform): handles the infrastructure. Domain teams: write dbt models and define SLOs. They don't manage Spark clusters, HDFS, or network configurations. The "self-serve" platform: abstracts infrastructure so domain engineers (Java/Python developers) can publish data products without data engineering infrastructure knowledge. |
| Data Mesh is better than data warehouse for all organizations | Data Mesh is appropriate for organizations where: (1) central data team is a demonstrated bottleneck, (2) domain teams are willing and able to own data quality, (3) platform investment is feasible. For organizations with < 10 domain teams, a well-run central data team with clear SLAs is simpler and equally effective. Data Mesh has high organizational overhead; smaller orgs will find it over-engineered. |

---

### 🚨 Failure Modes & Diagnosis

**Data quality degradation: domain team neglects data product SLOs**

**Symptom:**
Finance team: reports that payment analytics
are wrong. Quarterly revenue report: shows
$12M instead of expected $15M. Data Mesh
autopsy: `payments-domain/v1` had a dbt
transformation bug introduced 3 weeks ago
(wrong currency conversion). Payment Team:
did not notice (no monitoring on their data
product SLOs). Finance: used bad data for
3 weeks.

**Root Cause:**
Data Mesh: domain team responsible for data
product quality. But: Payment Team doesn't
have processes for monitoring data quality
(they monitor their API SLOs, not data SLOs).
No automated data quality tests in CI/CD.
Data product: published with bug undetected.

**Diagnosis:**
```
Data quality check (Great Expectations):
  payments_transactions_v1:
  - expect_column_values_to_be_between(
      column='amount_usd',
      min_value=0.01,
      max_value=50000)  # sanity bound
  - expect_column_sum_to_be_between(
      column='amount_usd',
      min_value=100000,   # daily minimum
      max_value=10000000) # daily maximum
  # This test: would have caught 25% revenue
  # drop in 3 weeks ago run
  
Freshness check (Airflow):
  if last_updated_at < now() - 2h:
    alert("payments data product stale")
    # SLO breach: page Payment Team
```

**Fix:**
```
Preventive: automated data quality tests in
dbt (required before data product publish)
CICD gate: dbt test failure -> block publish
Monitoring: Great Expectations + Airflow
alerts for SLO breaches (freshness, completeness)
Post-incident: data rollback from previous
versioned Delta Lake snapshot
```

---

### 🔗 Related Keywords

**Organizational context:**
- `Conway's Law in Microservices` - Data Mesh
  applies Conway's Law to analytical data
- `Team Topologies` - Data Mesh uses Platform
  team for data infrastructure
- `Service Ownership Model` - Data Mesh extends
  ownership to analytical data

**Technical context:**
- `Eventual Consistency` - data products have
  eventual consistency (freshness SLOs, not
  real-time)

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| PRINCIPLE 1  | Domain owns data (not just DB)  |
| PRINCIPLE 2  | Data as product (SLO, catalog)  |
| PRINCIPLE 3  | Self-serve platform (not ticket)|
| PRINCIPLE 4  | Federated governance (not silo) |
+--------------+---------------------------------+
| TECH STACK   | dbt + Delta Lake + Airflow      |
|              | + Data Catalog + Great Expects  |
+--------------+---------------------------------+
| WHEN NOT TO  | < 10 domains; central team not  |
| USE          | bottleneck; no platform invest  |
+--------------+---------------------------------+
| ONE-LINER    | "Microservices for data:        |
|              |  domain teams own their data    |
|              |  products end-to-end."          |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Four principles: Domain ownership, Data as
   product (SLO + catalog + schema), Self-serve
   platform, Federated governance.
2. Organizational prerequisite: domain teams must
   accept data quality responsibility. Technology
   alone doesn't create a Data Mesh.
3. Not for everyone: best for > 20 domain teams
   where central data team is a bottleneck.
   < 10 teams: centralized model is simpler.

**Interview one-liner:**
"Data Mesh (Dehghani, 2019): decentralized data
architecture applying microservices principles to
analytical data. Four principles: (1) Domain
ownership - domain teams own their analytical data
products, not just operational DBs; (2) Data as
a product - datasets have SLOs, schemas, owners,
are discoverable in catalog; (3) Self-serve data
platform - domain teams publish/consume data
without tickets to central team; (4) Federated
governance - central standards, domain execution.
Key challenge: organizational (getting domain teams
to own data quality), not technical. Not recommended
for < 10 domain teams; central data warehouse is
simpler at small scale."

---

### 💡 The Surprising Truth

Data Mesh's most important insight is not about
technology - it's that DATA QUALITY IS A PRODUCT
QUALITY ISSUE. In a centralized model: the central
data team produces the analytical data. When data
quality is poor: blame the data team. In Data Mesh:
the Payment Team produces `payments-domain/v1`.
When payment data quality is poor: the Payment
Team (who built the service that generates the
data) is responsible. This accountability shift
is profound: the team that generates the data
(payment engineers) understands it best, and they
are now accountable for its analytical quality.
This is exactly the same insight as "you build it,
you run it" (better reliability when devs are
oncall) applied to data. Domain engineers: write
better data transformations when they're responsible
for the downstream analytical quality of their
own data.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DATA PRODUCT SPEC** Write a data product
   specification for an orders domain: schema,
   SLOs (freshness, completeness, accuracy),
   owner, consumers, PII handling policy, and
   access control. Explain how this is a
   "product" rather than just a dataset.
2. **DBT MODEL** Write a dbt model that transforms
   raw orders DB data into an orders data product.
   Add dbt tests for: unique order_id, non-null
   required fields, amount range bounds,
   status accepted values. Explain how tests
   serve as data quality assertions.
3. **PLATFORM DESIGN** Design the minimum viable
   data platform for 5 domain teams: what
   self-serve capabilities are needed? What
   does "golden path to publish a data product"
   look like (< 1 day for a domain engineer
   to go from operational DB to published data
   product)?
4. **GOVERNANCE** A domain team accidentally
   published customer emails (PII) in their
   data product. Design: (1) automated prevention
   (policy as code), (2) detection mechanism,
   (3) incident response process, (4) retroactive
   access revocation.
5. **DECISION** Your company has 8 domain teams
   and a central data team of 5 engineers. Is
   Data Mesh the right architecture? Justify
   with specific criteria. If not now, at what
   scale does it become appropriate?

---

### 🧠 Think About This Before We Continue

**Q1.** A domain team (Payments) builds their
data product. After 3 months: Finance team
reports the data product has 5% missing transactions.
Payment Team: "the pipeline is running fine."
Finance Team: "the data is wrong." How do you
resolve this? What should have been in place
to prevent this disagreement? What is the
role of data contracts + SLOs in preventing
this failure?

**Q2.** Your organization decides to adopt
Data Mesh. Domain teams: 12 squads, each with
6-8 engineers. Current skill profile: all
are backend engineers (Java, Spring Boot). None
have dbt or analytical pipeline experience.
Design a 6-month enabling team engagement
to upskill all 12 teams. What does the enabling
team teach? What platform capabilities must
exist before the enabling team can start?
At what point do you consider a domain team
"ready" to publish a data product independently?

**Q3.** A consumer team (ML) depends on 5 data
products from 5 different domain teams. One
of the domain teams changes the schema of their
data product (removes a column that ML team uses).
ML model: breaks in production. In the centralized
model: schema changes go through central data
team review. In Data Mesh: how do you prevent
breaking schema changes? What is the Data Mesh
equivalent of CDC (Consumer-Driven Contracts)
for APIs?