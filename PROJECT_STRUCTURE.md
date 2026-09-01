# BATMAN - Project Structure

**Bitcoin Anomaly Traffic & Monitoring Analysis Network**

## Directory Structure

```
BATMAN/
├── src/
│   ├── core/backend/                    # Core analytics engine
│   │   ├── alerts/                      # Alert generation
│   │   ├── correlation/                 # Transaction correlation
│   │   ├── evaluation/                  # Model evaluation
│   │   ├── explainability/              # Model explainability
│   │   ├── features/                    # Feature engineering
│   │   ├── graph/                       # Graph analysis
│   │   ├── ingestion/                   # Data ingestion
│   │   ├── ml/                          # ML models & clustering
│   │   ├── output/                      # Output finalization
│   │   ├── risk/                        # Risk scoring
│   │   └── validation/                  # Data validation
│   ├── data/                            # Data management
│   ├── desktop_gui/                     # PySide6 Desktop GUI
│   ├── web_frontend/                    # Streamlit Web Interface
│   └── utils/                           # Shared utilities
│
├── tests/                               # Unit & integration tests
├── data/
│   ├── dev/                             # Development datasets
│   └── final/                           # Final processed data
├── config/                              # Configuration files
├── resources/                           # Static assets (fonts, images)
├── scripts/                             # Pipeline scripts
├── outputs/                             # Generated outputs (alerts, reports)
├── docs/                                # Documentation
├── main.py                              # Entry point: Desktop GUI
├── app.py                               # Entry point: Web Interface
├── requirements.txt                     # Python dependencies
└── .venv/                               # Python virtual environment
```

## Key Modules

### Core Backend (`src/core/backend/`)
- **ml/**: Isolation Forest, HDBSCAN clustering models
- **features/**: Wallet feature engineering & extraction
- **graph/**: Transaction graph building
- **ingestion/**: Data ingestion & parsing
- **alerts/**: Alert generation & entity flagging
- **evaluation/**: Model evaluation & validation
- **risk/**: Risk scoring & assessment
- **explainability/**: Model interpretability

### Interfaces
- **desktop_gui/**: PySide6 desktop application with graphs, charts, alerts
- **web_frontend/**: Streamlit web interface
- **data/**: Data management layer

## Entry Points
- `main.py` - Run desktop GUI
- `app.py` - Run web interface
- `scripts/run_step*.py` - Pipeline execution scripts

## Running the Application

```bash
# Desktop GUI (recommended)
python main.py

# Web Interface
streamlit run app.py
```

## Tests

Run all tests with: `pytest tests/`

Test files:
- `test_alerts.py` - Alert generation
- `test_clustering.py` - ML clustering
- `test_evaluation.py` - Model evaluation
- `test_features.py` - Feature engineering
- `test_ml.py` - ML models
- `test_ingestion.py` - Data ingestion
- etc.

