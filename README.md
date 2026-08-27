# BATMAN

**Bitcoin Anomaly Traffic & Monitoring Analysis Network**

Offline desktop investigation tool for analysing Bitcoin transaction traffic.
Built with PySide6 (Qt) and NetworkX.

---

## Requirements

- Python 3.10+
- Ubuntu/Linux (primary target)
- No internet access required at runtime

## Quick Start

```bash
cd BATMAN
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Or use the install script:

```bash
bash scripts/install_deps.sh
source .venv/bin/activate
python main.py
```

## Project Structure

```
BATMAN/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── gui/                             # PySide6 desktop GUI
│   ├── main_window.py               # Main window with sidebar + stacked pages
│   ├── sidebar.py                   # Navigation sidebar
│   ├── dev_data.py                  # Placeholder datasets (DEV only)
│   ├── pages/                       # One widget per navigation page
│   │   ├── overview_page.py
│   │   ├── alerts_page.py
│   │   ├── entity_investigation_page.py
│   │   ├── transaction_analysis_page.py
│   │   ├── network_graph_page.py
│   │   └── explainability_page.py
│   ├── widgets/                     # Reusable UI components
│   ├── graph/                       # NetworkX graph rendering (matplotlib)
│   └── charts/                      # Chart widgets
├── backend/                         # Analytical backend (Ankita)
├── data/                            # Datasets
├── frontend/                        # Streamlit prototype (reference only)
└── config/
```

## Navigation

| Page | Purpose |
|---|---|
| Overview | KPI cards, summary table, system health |
| Alerts | Filterable alert table with detail panel |
| Entity Investigation | Entity profile, timeline, network, evidence, explanation |
| Transaction Analysis | Transaction table, detail view, filters |
| Network Graph | Interactive NetworkX graph with controls |
| Explainability | Anomaly scores, feature importance, evidence, reasons |

## Team

- **Ankita** — AI/ML Backend
- **Janhavi** — Desktop GUI & Integration
- **Nutan** — Synthetic Dataset

SIH 2026 · Problem ID: SIH26146
