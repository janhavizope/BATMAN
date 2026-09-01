# SIH 2026 — RESEARCH, ARCHITECTURE & REFERENCES

## PROJECT

AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic

Problem identifier referenced in the project materials:

SIH26146

---

# 1. PROJECT OBJECTIVE

The project is an offline investigative decision-support system for analyzing synthetic Bitcoin transaction traffic and related Bitcoin P2P/network metadata.

The system should:

- Process synthetic Bitcoin transaction data
- Process network metadata
- Correlate transaction, wallet/address and network observations
- Detect anomalous behavior using AI/ML
- Identify behavioral clusters
- Calculate configurable risk scores
- Provide explanations and evidence
- Rank suspicious/anomalous entities
- Provide an investigation dashboard
- Run locally on Linux
- Work without Internet access during runtime

---

# 2. IMPORTANT PROJECT CONSTRAINT

The final tool must be:

OFFLINE

and

LINUX COMPATIBLE.

The system should not require Internet access during normal operation.

Avoid runtime dependence on:

- Cloud APIs
- Live blockchain APIs
- Live Bitcoin RPC
- Cloud AI APIs
- Online model inference
- Online dashboards
- CDN resources

The required models, libraries and data must be available locally.

---

# 3. DATA REQUIREMENT

The project uses SYNTHETIC DATA at the current development stage.

Expected dataset structure:

## Required fields

timestamp

src_ip

dst_ip

src_port

dst_port

txid

input_addresses[]

output_addresses[]

input_amounts[]

output_amounts[]

geo_country

asn

## Recommended fields

fee

script_type

block_height

block_timestamp

connection_duration

entity_id

## Ground-truth fields

is_suspicious

pattern_type

IMPORTANT:

Ground-truth fields are for evaluation.

They MUST NOT be used as ML input features.

---

# 4. SYNTHETIC DATA TARGET

The supplied project configuration describes an initial target approximately consisting of:

20,000 transactions

13,776 wallets/addresses

17,701 IPs

20–30 intentionally suspicious entities

The final dataset should contain both:

- Normal behavior
- Suspicious behavior

The final synthetic dataset is owned by Nutan.

---

# 5. SUSPICIOUS BEHAVIOR PATTERNS

The research/project material identifies patterns such as:

## Rapid transfer chain

Funds move through multiple entities in a short period.

## Fan-out

One entity distributes funds to many entities.

## Fan-in

Many entities send funds to one entity.

## Layering / multi-hop movement

Transactions move through multiple intermediate entities.

## Peeling chain

Repeated transfers progressively move portions of funds.

## High-frequency burst

Unusually high transaction activity within a short time period.

## Unusual amount distribution

Transaction amounts significantly differ from normal behavioral patterns.

## Repeated IP-wallet association

Repeated network association between wallets and IP observations.

## Shared network characteristics

Multiple wallets/entities display related network characteristics.

## Geographic/network anomalies

Unusual country, ASN or network behavior.

---

# 6. SYSTEM ARCHITECTURE

FINAL SYNTHETIC DATA
        ↓
DATA INGESTION
        ↓
VALIDATION
        ↓
NORMALIZATION
        ↓
IP ↔ TRANSACTION ↔ WALLET CORRELATION
        ↓
HETEROGENEOUS GRAPH
        ↓
FEATURE ENGINEERING
        ↓
AI / ML
        ↓
ANOMALY DETECTION
        ↓
BEHAVIORAL CLUSTERING
        ↓
RISK SCORING
        ↓
EXPLAINABILITY
        ↓
RANKED ALERTS
        ↓
INVESTIGATION DASHBOARD
        ↓
OFFLINE LINUX TOOL

---

# 7. DATA INGESTION

The system should support:

- CSV
- JSON
- XML

The ingestion layer should:

1. Load the dataset.
2. Validate the schema.
3. Normalize data types.
4. Handle missing values.
5. Detect invalid records.
6. Detect duplicates where appropriate.
7. Produce a data-quality result.

---

# 8. CORRELATION

The system should correlate:

IP
↕
Transaction
↕
Wallet

Additional relationships:

Wallet
↕
IP
↕
ASN
↕
Country

These correlations are investigative associations.

They must NOT automatically be interpreted as proof of ownership or criminal activity.

---

# 9. GRAPH ARCHITECTURE

Recommended initial graph technology:

NetworkX

Potential node types:

- Wallet
- Transaction
- IP
- ASN
- Country

Potential relationships:

Wallet → Transaction

Transaction → Wallet

Wallet → IP

IP → ASN

IP → Country

The graph should support multi-hop investigation.

---

# 10. FEATURE ENGINEERING

## Transaction features

- Transaction amount
- Fee
- Input count
- Output count
- Fee ratio
- Input/output ratio

## Wallet/entity features

- Total transaction count
- Incoming transaction count
- Outgoing transaction count
- Total received
- Total sent
- Average transaction amount
- Maximum transaction amount
- Minimum transaction amount
- Unique counterparties
- Wallet age

## Temporal features

- Transactions per hour
- Transactions per day
- Transaction velocity
- Inter-arrival time
- Burst frequency
- Short-interval transaction count

## Graph features

Potential features:

- Degree
- In-degree
- Out-degree
- PageRank
- Betweenness centrality
- Clustering coefficient
- K-core

## Network features

- Unique IP count
- Unique ASN count
- Unique country count
- IP-change frequency
- Peer count
- Destination-port distribution
- Network diversity

---

# 11. AI ARCHITECTURE

## Isolation Forest

Primary unsupervised anomaly-detection model.

Purpose:

Identify entities whose behavior differs significantly from the learned normal behavioral structure.

Input:

Behavioral/analytical features.

Do NOT use:

is_suspicious

or

pattern_type

as model input.

---

# 12. HDBSCAN

Preferred clustering approach:

HDBSCAN

Purpose:

Identify behavioral groups and unusual/low-density entities.

HDBSCAN results should be interpreted using actual feature behavior.

Do not simply assign a criminal meaning to a cluster number.

---

# 13. DBSCAN

DBSCAN can be used as a comparison baseline if time permits.

The purpose is comparison rather than replacing the primary HDBSCAN approach.

---

# 14. RISK SCORING

The supplied project configuration gives the following initial experimental weighting:

Anomaly Risk:

0.30

Graph Risk:

0.20

Temporal Risk:

0.15

Transaction Risk:

0.15

Network Risk:

0.10

Cluster Risk:

0.10

Total:

1.00

These weights should remain configurable.

They should not be presented as universally validated values.

---

# 15. RISK LEVELS

0–30:

LOW

31–60:

MEDIUM

61–80:

HIGH

81–100:

CRITICAL

The score represents investigative priority.

It is NOT proof of criminal activity.

---

# 16. EXPLAINABILITY

The system should explain why an entity received a high risk score.

Possible explanations:

- High transaction velocity
- Unusual graph degree
- High number of counterparties
- Unusual amount distribution
- Repeated IP association
- Unusual network diversity
- Unusual temporal behavior
- Cluster behavior significantly different from normal entities

Recommended approach:

SHAP

or another defensible explainability method.

---

# 17. ALERT STRUCTURE

Each alert should contain, where available:

- Rank
- Entity ID
- Risk score
- Risk level
- Anomaly score
- Cluster ID
- Top reasons
- Transaction count
- Counterparty count
- IP/ASN summary
- Evidence references
- Timestamp range

---

# 18. DASHBOARD ARCHITECTURE

## OVERVIEW

Display:

- Total transactions
- Total wallets
- Total IPs
- Anomalous entities
- High-risk entities
- Critical alerts

## ALERTS

Display:

- Ranked alerts
- Risk score
- Risk level
- Entity ID
- Main reason
- Filters

## ENTITY INVESTIGATION

Display:

- Entity profile
- Transaction history
- Timeline
- Incoming/outgoing activity
- Counterparties
- IP associations
- ASN
- Country
- Risk score
- Evidence
- Explanation

## GRAPH

Display:

- Wallets
- Transactions
- IPs
- ASNs
- Countries
- Relationships
- Multi-hop investigation

## EXPLAINABILITY

Display:

- Anomaly score
- Top contributing features
- Evidence
- Reasons for risk

---

# 19. EVALUATION

Final evaluation must use Nutan's final synthetic dataset and ground truth.

Possible metrics:

- Precision
- Recall
- F1-score
- ROC-AUC where meaningful
- Detection Rate
- False Positive Rate
- Precision@20
- Precision@50
- Recall@K

Possible comparison:

1. Rule-based baseline
2. Isolation Forest
3. HDBSCAN
4. Combined anomaly + graph + temporal + network risk system

IMPORTANT:

Never invent performance numbers.

Performance results should be calculated from the actual final dataset.

---

# 20. RECOMMENDED TECHNOLOGY STACK

Python

Pandas

NumPy

Scikit-learn

HDBSCAN

SHAP

NetworkX

Plotly

PySide6

SQLite / Parquet

Optional:

DuckDB

---

# 21. LINUX TOOL ARCHITECTURE

Target:

Ubuntu/Linux

Application:

PySide6 (Qt) Desktop GUI

Backend:

Python analytical modules

ML:

Scikit-learn + HDBSCAN

Graph:

NetworkX

Storage:

SQLite / Parquet

Visualization:

Plotly

Runtime:

LOCAL / OFFLINE

---

# 22. OFFLINE EXECUTION

The final tool should be capable of running after the required dependencies have been installed locally.

Example:

python main.py

Or as AppImage:

./BATMAN-x86_64.AppImage

No Internet connection should be required for:

- Loading data
- Running AI/ML
- Building graphs
- Calculating risk
- Generating alerts
- Investigating entities
- Viewing results

---

# 23. RECOMMENDED PROJECT STRUCTURE

bitcoin-monitor/

├── main.py
├── requirements.txt
├── README.md
│
├── config/
│   └── config.yaml
│
├── data/
│   ├── dev/
│   └── final/
│
├── backend/
│   ├── ingestion/
│   ├── validation/
│   ├── correlation/
│   ├── features/
│   ├── graph/
│   ├── ml/
│   ├── risk/
│   └── explainability/
│
├── desktop_gui/
│   ├── main_window.py
│   ├── sidebar.py
│   ├── pages/
│   │   ├── overview_page.py
│   │   ├── alerts_page.py
│   │   ├── entity_investigation_page.py
│   │   ├── transaction_analysis_page.py
│   │   ├── network_graph_page.py
│   │   └── explainability_page.py
│   ├── widgets/
│   ├── charts/
│   └── state/
│
├── models/
│
├── tests/
│
└── scripts/

---

# 24. RESEARCH REFERENCES PROVIDED BY THE TEAM

## Research papers / academic sources

https://www.nature.com/articles/s41597-025-04684-8

https://ieeexplore.ieee.org/document/11311752

https://arxiv.org/pdf/1502.01657

https://arxiv.org/abs/1908.02591

https://arxiv.org/abs/2306.06108

https://arxiv.org/abs/2404.19109

https://pmc.ncbi.nlm.nih.gov/articles/PMC9005027/

https://ijirt.org/publishedpaper/IJIRT205094_PAPER.pdf

https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7004983

---

# 25. INDUSTRY / BLOCKCHAIN ANALYSIS REFERENCES

https://hdiac.dtic.mil/articles/real-time-cryptocurrencies-monitoring-for-criminal-activity-detection-a-comprehensive-system/

https://www.trmlabs.com/resources/blog/ais-role-in-blockchain-intelligence-network-discovery-pattern-recognition-and-investigative-acceleration

https://hawk.ai/industries/cryptocurrency

https://www.tcs.com/what-we-do/research/white-paper/ai-crypto-money-laundering-detection

https://automatio.ai/use-cases/cryptocurrency-data-analysis

https://bitquery.io/blog/best-blockchain-analysis-tools-and-software-tools

---

# 26. BITCOIN BACKGROUND REFERENCES

https://www.investopedia.com/news/how-bitcoin-works/

https://www.investopedia.com/ask/answers/063015/what-does-block-chain-record-bitcoin-exchange-transaction.asp

---

# 27. LAW-ENFORCEMENT / REAL-WORLD CASE REFERENCES

https://www.justice.gov/archives/opa/pr/department-justice-seizes-23-million-cryptocurrency-paid-ransomware-extortionists-darkside

https://www.justice.gov/usao-or/pr/russian-cryptocurrency-money-launderer-pleads-guilty

https://www.justice.gov/usao-dc/case/united-states-v-ilya-lichtenstein-and-heather-morgan

https://www.justice.gov/usao-dc/pr/jury-finds-russian-swedish-operator-bitcoin-fog-guilty-running-darknet-cryptocurrency-mixer

https://www.justice.gov/archives/opa/pr/justice-department-investigation-leads-takedown-darknet-cryptocurrency-mixer-processed-over-323

These sources provide real-world context for cryptocurrency investigations.

They should not be interpreted as evidence that synthetic entities in our project represent real criminal actors.

---

# 28. TEAM-PROVIDED SOURCE FILES

The project materials supplied by the team are:

- Reference links.txt
- Research file.docx
- Project Configuration file.docx
- architecture.md

These should be retained in the project/reference material.

---

# 29. RESEARCH DISCIPLINE

When adding new research:

- Record the source.
- Record what the source actually supports.
- Separate source-backed facts from assumptions.
- Do not invent research findings.
- Do not invent model performance.
- Do not treat a correlation as proof of ownership.
- Do not treat an anomaly score as proof of criminality.
- Clearly distinguish synthetic data from real-world blockchain data.

---

# 30. FINAL ARCHITECTURE

                    ┌───────────────────────┐
                    │ FINAL SYNTHETIC DATA  │
                    │       NUTAN           │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ INGESTION + VALIDATION│
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ CORRELATION           │
                    │ IP ↔ TX ↔ WALLET      │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ GRAPH + FEATURES      │
                    │       ANKITA          │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ AI / ML               │
                    │ Isolation Forest      │
                    │ HDBSCAN               │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ RISK + EXPLAINABILITY │
                    │       ANKITA          │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ OFFLINE TOOL          │
                    │       JANHAVI         │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ DASHBOARD             │
                    │ ALERTS                │
                    │ INVESTIGATION         │
                    │ GRAPH                 │
                    │ EXPLANATION           │
                    └───────────────────────┘