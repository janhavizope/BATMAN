# SIH 2026 — TEAM RESPONSIBILITIES & WORK BOUNDARIES

## PROJECT

AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic

This document defines the responsibilities of:

1. Janhavi
2. Ankita
3. Nutan

The purpose is to ensure that each person works only on their assigned responsibility and that the same work is not duplicated.

---

# 1. JANHAVI — PERSON 2

## ROLE

Tool Development, Integration, Investigation Dashboard & Offline Linux

## JANHAVI'S RESPONSIBILITIES

Janhavi is responsible for building the actual offline tool/interface that the user will operate.

### Main responsibilities:

- Streamlit application
- Application structure
- Dashboard
- Overview page
- Alert dashboard
- Alert filtering
- Entity investigation interface
- Transaction investigation interface
- Graph visualization/interface
- Explainability presentation
- Displaying AI-generated results
- Backend integration
- Connecting Ankita's analytical output to the tool
- Dataset loading interface
- Analysis execution interface
- Application status/progress
- Linux/Ubuntu compatibility
- Offline execution testing
- Application-level testing
- Final demonstration workflow
- README/run instructions
- Final tool integration

### Janhavi's workflow:

Ankita's AI/analysis output
        ↓
Janhavi's integration
        ↓
Dashboard
        ↓
Ranked alerts
        ↓
Entity investigation
        ↓
Graph visualization
        ↓
Risk explanation
        ↓
Offline Linux tool

---

# 2. ANKITA — PERSON 1

## ROLE

AI/ML, Data Analysis & Analytical Backend

## ANKITA'S RESPONSIBILITIES

Ankita is responsible for building the analytical and AI/ML backend of the system.

### Main responsibilities:

- Data ingestion backend
- CSV/JSON/XML processing
- Data validation
- Data normalization
- IP ↔ transaction ↔ wallet correlation
- Analytical graph construction
- NetworkX graph logic
- Feature engineering
- Transaction features
- Wallet/entity features
- Temporal features
- Graph features
- Network features
- Isolation Forest
- HDBSCAN
- DBSCAN baseline if required
- Anomaly detection
- Behavioral clustering
- Risk-score calculation
- Risk engine
- Explainability calculations
- AI evaluation
- Model testing
- Backend testing
- Producing structured output for Janhavi

### Ankita's workflow:

Dataset
        ↓
Validation
        ↓
Normalization
        ↓
Correlation
        ↓
Graph
        ↓
Feature Engineering
        ↓
Isolation Forest
        ↓
HDBSCAN
        ↓
Risk Score
        ↓
Explainability
        ↓
Ranked Results
        ↓
Janhavi's Tool

---

# 3. NUTAN — PERSON 3

## ROLE

Final Synthetic Dataset Generation

## NUTAN'S RESPONSIBILITIES

Nutan is responsible for creating and delivering the final synthetic dataset required by the project.

### Main responsibilities:

- Synthetic Bitcoin transaction dataset
- Synthetic Bitcoin network/P2P data
- Normal behavior generation
- Suspicious behavior generation
- Suspicious transaction patterns
- Ground-truth labels
- Final dataset preparation
- Dataset consistency
- Dataset delivery
- Final dataset documentation

### Suspicious behavior may include:

- Rapid transfer chains
- Fan-in
- Fan-out
- Layering/multi-hop movement
- Peeling chains
- High-frequency transaction bursts
- Unusual transaction amounts
- Repeated IP-wallet associations
- Multiple wallets sharing network characteristics
- Geographic/network anomalies

### IMPORTANT

Nutan owns the FINAL synthetic dataset.

Janhavi and Ankita must not replace or take over Nutan's final dataset-generation work.

They may:

- Define required fields
- Discuss dataset requirements
- Test whether the dataset works with the system
- Report dataset-related bugs

But final synthetic-data generation remains Nutan's responsibility.

---

# 4. STRICT WORK-BOUNDARY RULE

Every team member must work only on their assigned responsibilities.

Do not duplicate another person's main work.

Do not silently modify another person's component.

Do not take over another person's responsibility simply because it looks easier or faster.

---

# 5. JANHAVI ENTERS ANKITA'S WORK

If Janhavi starts doing work belonging to Ankita, STOP immediately.

Display this message:

"BOUNDARY WARNING: You are doing Ankita's work. Stop here and let Ankita handle the AI/ML and analytical backend work. Once Ankita provides the output, you can continue with the integration and tool development."

This applies to:

- Isolation Forest
- HDBSCAN
- DBSCAN
- Feature engineering
- ML model training
- ML model tuning
- Analytical graph construction
- Risk-score calculation
- AI evaluation
- Backend analytical logic

Janhavi should request the required output from Ankita instead of implementing it herself.

---

# 6. ANKITA ENTERS JANHAVI'S WORK

If Ankita starts doing work belonging to Janhavi, STOP immediately.

Display this message:

"BOUNDARY WARNING: You are doing Janhavi's work. Stop here and let Janhavi handle the tool, dashboard, UI and integration work. Provide the required backend output to Janhavi and continue with your AI/ML work."

This applies to:

- Streamlit pages
- Dashboard
- Alert UI
- Entity investigation UI
- Frontend navigation
- Graph visualization UI
- Explainability UI
- UI styling
- Final application interface
- Tool workflow

Ankita should provide backend results/interfaces instead of building Janhavi's frontend.

---

# 7. JANHAVI OR ANKITA ENTERS NUTAN'S WORK

If Janhavi or Ankita starts creating or replacing the FINAL synthetic dataset, STOP immediately.

Display this message:

"BOUNDARY WARNING: You are doing Nutan's work. Stop here and let Nutan handle the final synthetic dataset generation. You may only define the required schema or test the dataset after Nutan provides it."

This applies to:

- Final synthetic dataset generation
- Final suspicious labels
- Final normal/suspicious behavior generation
- Replacing Nutan's dataset
- Redesigning Nutan's final generator

---

# 8. TEMPORARY DEVELOPMENT DATA

If Nutan is not available during early development, Janhavi or Ankita may create a very small temporary development fixture only when required for software testing.

This data must:

- Be clearly labelled DEVELOPMENT DATA
- Be stored separately
- Not be treated as the final SIH dataset
- Not be used for final performance claims
- Not replace Nutan's final dataset
- Not be mixed with the final dataset

Once Nutan provides the final synthetic dataset, the final dataset must be used for final evaluation.

---

# 9. SHARED WORK

The following work may be performed together:

- Project architecture discussions
- Input schema
- Backend/UI output contract
- Configuration
- requirements.txt
- Testing across components
- Git integration
- Documentation
- Security
- Linux compatibility
- Reproducibility
- Final integration
- Bug reporting

However, shared work does not mean taking ownership of another person's main component.

---

# 10. IF A BUG IS FOUND IN ANOTHER PERSON'S WORK

Do NOT immediately rewrite their code.

Follow this process:

1. Identify the problem.
2. Reproduce the problem.
3. Explain the problem.
4. Inform the responsible person.
5. Hand the problem to that person.
6. Wait for their implementation/fix.
7. Continue your own work.

Example:

Janhavi finds an Isolation Forest problem.

Janhavi should NOT rewrite the Isolation Forest.

She should tell Ankita:

"Isolation Forest output is producing an unexpected result. Please check the model/backend."

Ankita fixes it.

Then Janhavi continues integration.

---

# 11. FINAL TEAM STRUCTURE

ANKITA
=
AI / ML / ANALYTICAL BRAIN

JANHAVI
=
OFFLINE TOOL / DASHBOARD / INVESTIGATION INTERFACE

NUTAN
=
FINAL SYNTHETIC DATASET

---

# 12. SIMPLE RULE

ANKITA BUILDS THE BRAIN.

JANHAVI BUILDS THE TOOL.

NUTAN BUILDS THE FINAL DATA.

DO NOT CROSS THE BOUNDARY.

If you start doing another person's work:

STOP.

Show the boundary-warning message.

Hand the work to the correct person.

Then continue with your own responsibility.

---

# 13. FINAL OBJECTIVE

The three responsibilities eventually connect as:

NUTAN
Final Synthetic Dataset
        ↓
ANKITA
AI/ML + Analysis + Risk + Evidence
        ↓
JANHAVI
Offline Linux Investigation Tool
        ↓
FINAL SIH PROJECT