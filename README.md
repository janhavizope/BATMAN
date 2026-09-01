# BATMAN — Bitcoin Anomaly Traffic & Monitoring Analysis Network

**AI-Powered Offline Anomaly Detection & Investigation Tool for Bitcoin Transaction Analysis**

## 🔍 Problem Statement

**Problem ID:** SIH26146  
**Theme:** AI/Blockchain & Cyber Security  
**Category:** Software  
**Organization:** Smart India Hackathon 2026

### The Challenge
Bitcoin and cryptocurrency transactions are increasingly exploited by threat actors, money launders, and malicious entities to transfer illicit funds while evading detection. Traditional analysis methods are manual, time-consuming, and prone to human error.

**What We Needed:**
- An offline, Linux-compatible system for analyzing Bitcoin transaction traffic
- Automated detection of anomalous wallet behaviors and suspicious patterns
- AI/ML-powered risk scoring and explainability
- Real-time alerting with investigative evidence
- Dashboard for SOC analysts to prioritize and investigate entities

---

## ✨ What is the Project?

**BATMAN** is a comprehensive **offline investigative decision-support system** designed to detect anomalous Bitcoin entities and suspicious transaction patterns using advanced ML, graph analytics, and behavioral profiling.

The system integrates:
- **Data Ingestion Pipeline** — Processes synthetic Bitcoin transaction datasets
- **Feature Engineering Engine** — Extracts 30+ financial, temporal, and graph-based features per wallet
- **Anomaly Detection Models** — Isolation Forest for outlier detection, HDBSCAN for behavioral clustering
- **Risk Scoring & Ranking** — Calculates risk scores and ranks entities by suspicion level
- **Explainability Module** — Provides human-readable evidence for why entities are flagged
- **Desktop Investigation Platform** — PySide6 Desktop GUI

**Completely offline. No internet. No cloud APIs. Runs locally on Linux.**

---

## 🎯 The Problem We Solve

Bitcoin transactions are pseudo-anonymous, making it difficult to identify illicit activity:

📊 **Massive Data Volume** — Millions of transactions, impossible to analyze manually  
🔗 **Complex Patterns** — Suspicious entities use sophisticated laundering techniques  
🚨 **Late Detection** — Manual analysis delays incident response  
❓ **No Explainability** — Traditional ML models don't explain their decisions  
🌐 **Hidden Relationships** — Network effects and cascading activities are invisible  

**BATMAN detects:**
- **Fan-out attacks** — One wallet rapidly distributing funds to multiple newly-created wallets
- **Fan-in aggregation** — Multiple wallets consolidating funds into a single entity
- **High-velocity transactions** — Abnormal transaction frequency and speed
- **Behavioral anomalies** — Wallets deviating from their cluster's typical patterns
- **Network clustering** — Identifying groups of related entities with similar behaviors
- **Risk-scored entities** — Ranking wallets by suspicion severity

---

## ✅ Key Features

### 🎯 **ML-Powered Anomaly Detection**
- **Isolation Forest** identifies statistical outliers in wallet behavior
- **HDBSCAN Clustering** groups entities into behavioral clusters
- Detects both known patterns (supervised) and zero-day anomalies (unsupervised)

### 📊 **30+ Engineered Features**
- **Financial**: Transaction amounts, fees, value uniformity, fan-out/fan-in degrees
- **Temporal**: Transaction velocity, inter-arrival times, burst frequency
- **Graph-based**: Degree, centrality, PageRank, k-core, clustering coefficient
- **Network**: Unique IP counts, ASN diversity, geographic spread

### 🔍 **Real-Time Investigation Dashboard**
- **Overview Page** — KPI cards, aggregate statistics, entity rankings
- **Alerts Page** — Filterable, sortable alert table with severity levels
- **Entity Investigation** — Full entity profile, timeline, network graph, evidence panel
- **Transaction Analysis** — Detailed transaction table with drill-down capabilities
- **Network Graph** — Interactive NetworkX visualization with zoom, pan, hover info
- **Explainability** — Feature importance, contribution scores, human-readable reasons

### 🧠 **Interpretability & Evidence**
- Statistical z-score analysis identifies top contributing features
- Human-readable explanations for every anomaly flag
- MITRE-style threat classifications (optional enhancement)
- Ranked evidence cards supporting risk decisions

### 🖥️ **Dual-Interface Platform**
- **Desktop GUI** (PySide6/Qt) — Full-featured, native application for Linux

### ⚡ **Fully Offline Operation**
- No internet access required at runtime
- All models, libraries, and data stored locally
- No cloud API dependencies
- GDPR-compliant, on-premises deployment ready

---

## 🏗️ System Architecture

### Application Structure

```
┌────────────────────────────────────────┐
│       BATMAN Analysis Platform         │
├────────────────────────────────────────┤
│                                        │
│         ┌──────────────┐               │
│         │  Desktop GUI │               │
│         │  (PySide6)   │               │
│         └──────┬───────┘               │
│                    │                  │
│         ┌──────────▼──────────┐       │
│         │  Data Management    │       │
│         │  & State Layer      │       │
│         └──────────┬──────────┘       │
│                    │                  │
│  ┌─────────────────▼─────────────────┐│
│  │   Core Analytics Engine           ││
│  ├───────────────────────────────────┤│
│  │ • Data Ingestion & Validation     ││
│  │ • Feature Engineering (30+ feats) ││
│  │ • Graph Building (NetworkX)       ││
│  │ • Anomaly Detection (IF, HDBSCAN) ││
│  │ • Risk Scoring & Ranking          ││
│  │ • Explainability & Evidence       ││
│  └───────────────────────────────────┘│
│                                        │
│  ┌────────────────────────────────────┐│
│  │      Data Layer                    ││
│  │  • Bitcoin Transactions (Parquet)  ││
│  │  • Engineered Features (Parquet)   ││
│  │  • Anomaly Scores                  ││
│  │  • Alerts & Rankings               ││
│  └────────────────────────────────────┘│
└────────────────────────────────────────┘
```

### Directory Structure

```
BATMAN/
├── src/
│   ├── core/backend/                    # Analytics engine
│   │   ├── ingestion/                   # Data loading & validation
│   │   ├── features/                    # Feature engineering
│   │   ├── graph/                       # Graph building & analysis
│   │   ├── ml/                          # ML models (Isolation Forest, HDBSCAN)
│   │   ├── risk/                        # Risk scoring
│   │   ├── explainability/              # Interpretability & evidence
│   │   ├── correlation/                 # Transaction correlation
│   │   ├── evaluation/                  # Model evaluation
│   │   ├── validation/                  # Data validation
│   │   ├── alerts/                      # Alert generation
│   │   └── output/                      # Output finalization
│   │
│   ├── desktop_gui/                     # PySide6 desktop interface
│   │   ├── main_window.py               # Main application window
│   │   ├── sidebar.py                   # Navigation sidebar
│   │   ├── pages/                       # Investigation pages
│   │   │   ├── overview_page.py         # Dashboard
│   │   │   ├── alerts_page.py
│   │   │   ├── entity_investigation_page.py
│   │   │   ├── transaction_analysis_page.py
│   │   │   ├── network_graph_page.py
│   │   │   └── explainability_page.py
│   │   ├── widgets/                     # Reusable UI components
│   │   ├── charts/                      # Data visualizations
│   │   └── state/                       # State management
│   │
│   ├── data/                            # Data management layer
│   └── utils/                           # Shared utilities
│
├── tests/                               # Unit & integration tests
├── data/                                # Datasets
│   ├── dev/                             # Development/synthetic data
│   └── final/                           # Final analysis results
├── scripts/                             # Pipeline scripts
├── outputs/                             # Generated alerts & reports
├── docs/                                # Research & references
├── main.py                              # Desktop GUI entry point
└── requirements.txt                     # Python dependencies
```

---

## 🔄 How It Works

### 1️⃣ Data Ingestion
- Load synthetic Bitcoin transaction CSV with transaction metadata
- Validate schema and data types
- Parse network information (IP, ASN, geolocation)

### 2️⃣ Graph Construction
- Build directed transaction graph (NetworkX DiGraph)
- Nodes = wallet addresses, Edges = fund transfers
- Compute graph metrics (PageRank, centrality, clustering)

### 3️⃣ Feature Engineering
Extract 30+ features per wallet:
- **Financial**: Total sent/received, average amounts, fee patterns
- **Temporal**: Transaction velocity, inter-arrival times, burst patterns
- **Network**: Geographic diversity, ASN distribution, IP overlap
- **Graph**: Degree, centrality measures, k-core decomposition

### 4️⃣ Anomaly Detection
- **Isolation Forest** scores each wallet (lower = more anomalous)
- Identifies statistical outliers in feature space
- Unsupervised learning — no labeled training data required

### 5️⃣ Behavioral Clustering
- **HDBSCAN** groups similar wallets into behavioral clusters
- Identifies wallets sharing suspicious patterns
- Enables relative risk scoring within clusters

### 6️⃣ Risk Scoring & Ranking
- Combine anomaly scores, cluster context, and feature deviations
- Generate composite risk score (0–100)
- Rank entities by suspicion severity (Critical → Medium → Low)

### 7️⃣ Explainability
- Identify top 3 features contributing to anomaly classification
- Calculate feature contribution using z-scores
- Generate human-readable explanations

### 8️⃣ Alert Generation
- Create alert records for flagged entities
- Include severity, risk score, evidence, explanations
- Display in investigation dashboard

### 9️⃣ Investigation & Response
- Analysts review alerts in dashboard
- Drill into entity profiles, timelines, network visualization
- Export evidence for reporting or escalation

---

## 🧠 Analysis Techniques

### Isolation Forest (Unsupervised Anomaly Detection)
**How It Works:**
- Randomly selects features and split values to isolate observations
- Anomalies require fewer splits to isolate (shorter average path length)
- Raw scores: negative = anomalous, positive = normal

**Why It Works:**
- No labeled training data required
- Handles high-dimensional feature spaces efficiently
- Effective for rare/novel threats (zero-day patterns)

### HDBSCAN (Hierarchical Clustering)
**How It Works:**
- Builds a dendrogram of density-connected clusters
- Extracts clusters at different density thresholds
- Assigns noise points to nearest cluster or marks as outliers

**Why It Works:**
- Identifies variable-density clusters (unlike K-means)
- Doesn't require pre-specifying cluster count
- Reveals natural behavioral groupings in data

### Graph Analytics (NetworkX)
**Key Metrics:**
- **PageRank** — Importance based on incoming fund transfers
- **Betweenness Centrality** — How often wallet bridges transaction paths
- **Clustering Coefficient** — Local density of wallet connections
- **K-Core** — Resilience/entrenchment in the network

**Interpretations:**
- High PageRank = Central laundering hub
- High betweenness = Bridge/mixer function
- Low clustering = Isolated suspicious node

### Statistical Interpretation (Z-Score Analysis)
**Method:**
- Normalize features using z-score: $(x - \mu) / \sigma$
- Identify features most deviating from cluster mean
- Rank by absolute z-score magnitude

**Benefit:**
- Mathematically grounded evidence
- Easy to explain to stakeholders
- Reproducible across runs

---

## 🔧 Tech Stack

| Category | Technologies |
|----------|---------------|
| **Backend Analytics** | Python 3.10+, Pandas, NumPy, scikit-learn |
| **ML/Anomaly Detection** | Isolation Forest, HDBSCAN, scikit-learn |
| **Graph Analysis** | NetworkX, graph algorithms |
| **Desktop UI** | PySide6 (Qt), Matplotlib, Plotly |
| **Data Storage** | Parquet (Apache Arrow), CSV |
| **Testing** | pytest, unittest |
| **Deployment** | Linux, Docker-ready |
| **Version Control** | Git |

---

## 📋 Project Features & Coverage

### Implemented Features ✅
- ✅ Full data ingestion & validation pipeline
- ✅ 30+ engineered features (financial, temporal, graph, network)
- ✅ Isolation Forest anomaly detection
- ✅ HDBSCAN behavioral clustering
- ✅ Risk scoring & entity ranking
- ✅ Statistical explainability (z-score analysis)
- ✅ PySide6 desktop GUI with 6 investigation pages
- ✅ Interactive NetworkX graph visualization
- ✅ Comprehensive unit & integration tests
- ✅ Fully offline operation (no cloud dependencies)


## 📊 Sample Analysis Results

### Detection Coverage
The system successfully detects:
- **Fan-out attacks** — 1 wallet → 8+ wallets in minutes
- **Fan-in aggregation** — 10+ wallets → 1 consolidation wallet
- **High-velocity transactions** — 50+ txs/hour vs. cluster avg 10 txs/day
- **Temporal anomalies** — Sudden bursts, unusual timing patterns
- **Geographic anomalies** — Transactions from unexpected countries
- **Network anomalies** — Unusual centrality, bridge functions

### Risk Score Distribution
- **Critical** (90–100): Most anomalous entities, multiple red flags
- **High** (70–89): Significantly anomalous, concerning patterns
- **Medium** (50–69): Slightly unusual, worth investigating
- **Low** (0–49): Normal behavior, low suspicion

---

## 🚀 Quick Start

### Requirements (Ubuntu/Linux)
- Ubuntu 18.04+ or equivalent Linux distribution
- ~2GB RAM for typical datasets
- ~1GB disk space (AppImage)

### Installation & Launch

**BATMAN is distributed as a standalone AppImage** — no Python installation needed!

#### Step 1: Download
Download `BATMAN-x86_64.AppImage` to your Downloads folder:
```bash
cd ~/Downloads
```

#### Step 2: Make Executable
```bash
chmod +x BATMAN-x86_64.AppImage
```

#### Step 3: Run
```bash
./BATMAN-x86_64.AppImage
```

That's it! 🎉 The application will launch with the full GUI.

---

### For Developers (Source Installation)

If you want to modify the source code:

```bash
# Clone repository
git clone <repo-url>
cd BATMAN

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

**Run Tests:**
```bash
pytest tests/ -v
```

---



## 📚 Research & References

### Academic Papers & Standards
| Type | Source | Topic |
|------|--------|-------|
| RFC | RFC 6979 — Deterministic ECDSA | Bitcoin cryptography |
| Research | Meiklejohn et al. (2013) — "A Fistful of Bitcoins" | Bitcoin address clustering |
| Research | Androulaki et al. (2013) — "Evaluating User Privacy in Bitcoin" | Deanonymization techniques |
| Industry | Chainalysis — Blockchain Intelligence Platform | Commercial reference |
| Industry | Elliptic — Cryptocurrency Risk Scoring | Enterprise approach |

### Bitcoin & Blockchain Resources
- Bitcoin Dev Kit (BDK) — Transaction parsing & validation
- Blockchain.com Data API — Reference for feature definitions
- MITRE ATT&CK — Threat framework (optional enhancement)

### ML & Graph Analytics
- scikit-learn Documentation — Isolation Forest details
- HDBSCAN Paper — Density-based clustering
- NetworkX Documentation — Graph algorithms
- Pandas & NumPy — Data manipulation

### Project References
- SIH 2026 Problem ID: **SIH26146**
- GitHub Repository: `BATMAN` (Smart India Hackathon)
- Development Methodology: Agile with TDD

---

## 🔐 Security & Privacy

- ✅ **Offline Operation** — No data transmission
- ✅ **GDPR-Compliant** — No cloud storage dependencies
- ✅ **Local Storage** — All data remains on-premises
- ✅ **No API Keys** — No external authentication required
- ✅ **Reproducible** — Deterministic anomaly detection

---

## 🎓 Educational Value

This project demonstrates:
- **ML/AI**: Anomaly detection, clustering, feature engineering
- **Graph Analytics**: NetworkX, centrality measures, PageRank
- **Data Engineering**: ETL pipelines, feature stores, data validation
- **Software Engineering**: Modular architecture, separation of concerns, testing
- **UI/UX**: PySide6 desktop applications with professional styling
- **Scientific Computing**: Pandas, NumPy, statistical analysis

---

## 👥 Team

### Team Lead
🧑‍💼 **Janhavi Zope**  

### Team Members
👩‍💻 **Ankita Khokhar**

👩‍💻 **Nutanapushpa Vasarla**

👩‍💻 **Neha More**

👩‍💻 **Lakshmi Sai Lekhana Bavikatta** 

👩‍💻 **Keziah Ann Mathew** 
---

## 📝 License & Attribution

Built for **Smart India Hackathon 2026**  
Problem ID: **SIH26146**  
Institution: **Symbiosis Skills And Professional University**

---

## 📧 Support & Documentation

For implementation details, architecture rationale, and research references, see:
- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) — Directory organization
- [`docs/RESEARCH_ARCHITECTURE_REFERENCES.md`](docs/RESEARCH_ARCHITECTURE_REFERENCES.md) — Technical background
- [`requirements.txt`](requirements.txt) — Dependencies and versions

---

**BATMAN — Making Bitcoin Transaction Analysis Transparent, Explainable, and Accessible** 🦇
