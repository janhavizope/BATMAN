"""
evaluate_model.py
Evaluates the unsupervised anomaly detection and clustering pipeline's performance
against ground-truth synthetic adversaries. Generates and saves a detailed report.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    confusion_matrix, classification_report
)

# Ensure backend packages can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def load_ground_truth(path: str) -> pd.Series:
    """Load wallet-level suspicious labels indexed by wallet address."""
    ground_truth = pd.read_parquet(path)
    if ground_truth.index.name == "wallet_address":
        ground_truth = ground_truth.reset_index()
    if "wallet_address" not in ground_truth.columns:
        raise ValueError("ground_truth.parquet must contain wallet_address as a column or index.")
    if "is_suspicious" not in ground_truth.columns:
        raise ValueError("ground_truth.parquet must contain an is_suspicious column.")

    labels = ground_truth.set_index("wallet_address")["is_suspicious"]
    return labels.astype(bool)


def generate_report(df: pd.DataFrame, ground_truth: pd.Series | pd.DataFrame | None = None) -> str:
    """
    Computes performance metrics and returns a formatted text report string.
    """
    # 1. Align the wallet-level ground-truth labels with the evaluated entities.
    if ground_truth is None:
        raise ValueError("Explicit wallet-level ground truth is required for evaluation.")
    if isinstance(ground_truth, pd.DataFrame):
        if "wallet_address" in ground_truth.columns:
            ground_truth = ground_truth.set_index("wallet_address")
        if "is_suspicious" not in ground_truth.columns:
            raise ValueError("Ground-truth dataframe must contain an is_suspicious column.")
        ground_truth = ground_truth["is_suspicious"]

    evaluation_df = df
    if "wallet_address" in evaluation_df.columns:
        evaluation_df = evaluation_df.set_index("wallet_address")
    missing_wallets = evaluation_df.index.difference(ground_truth.index)
    if len(missing_wallets):
        raise ValueError(f"Ground truth is missing {len(missing_wallets)} evaluated wallet labels.")
    y_true = ground_truth.reindex(evaluation_df.index).astype(bool).astype(int).values
    
    # 2. Create Predicted Label (1 if risk_flag is HIGH or MEDIUM, else 0)
    y_pred = df["risk_flag"].apply(lambda flag: 1 if flag in ["HIGH", "MEDIUM"] else 0).values
    
    # Calculate metrics
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    class_report = classification_report(y_true, y_pred, target_names=["Normal", "Suspicious"], zero_division=0)
    
    # Count variables
    total_entities = len(df)
    total_adversaries = int(sum(y_true))
    total_normal = total_entities - total_adversaries
    
    flagged_high = int((df["risk_flag"] == "HIGH").sum())
    flagged_med = int((df["risk_flag"] == "MEDIUM").sum())
    flagged_low = int((df["risk_flag"] == "LOW").sum())
    
    # Format confusion matrix
    tn, fp, fn, tp = cm.ravel()
    
    report_text = f"""======================================================================
BITCOIN TRANSACTION MONITORING — MODEL EVALUATION REPORT
======================================================================

1. DATASET OVERVIEW
----------------------------------------------------------------------
Total Wallet Entities   : {total_entities}
Actual Adversaries (GT) : {total_adversaries}
Actual Normal Wallets   : {total_normal}

System Risk Flags Assigned:
- HIGH Risk Flags       : {flagged_high}
- MEDIUM Risk Flags     : {flagged_med}
- LOW Risk Flags        : {flagged_low}

2. METRICS DEFINITIONS FOR NON-TECHNICAL AUDIENCES
----------------------------------------------------------------------
* PRECISION: "Out of all wallets flagged as suspicious by our system, 
             how many were actually real adversaries?"
             - A high precision (e.g. 90%) means very few false alarms.
             - Formula: True Positives / (True Positives + False Positives)

* RECALL:    "Out of all actual adversaries present in the dataset, 
             how many did our system succeed in catching?"
             - A high recall (e.g. 95%) means the system missed very few threats.
             - Formula: True Positives / (True Positives + False Negatives)

* F1-SCORE:  "The harmonic average of Precision and Recall."
             - It provides a single balanced metric measuring model effectiveness.

3. OVERALL EVALUATION METRICS
----------------------------------------------------------------------
Precision : {precision:.4f} ({precision*100:.1f}%)
Recall    : {recall:.4f} ({recall*100:.1f}%)
F1-Score  : {f1:.4f} ({f1*100:.1f}%)

4. CONFUSION MATRIX (CLASSIFICATION TALLY)
----------------------------------------------------------------------
                      Predicted Normal       Predicted Suspicious
Actual Normal         {tn:<22} {fp:<22} (False Alarms)
Actual Adversary      {fn:<22} (Missed)      {tp:<22} (Caught)

Summary:
- Correctly identified Normal wallets (True Negatives)  : {tn}
- False alarms raised on Normal wallets (False Positives): {fp}
- Missed actual threats (False Negatives)               : {fn}
- Correctly caught actual threats (True Positives)      : {tp}

5. DETAILED CLASSIFICATION REPORT
----------------------------------------------------------------------
{class_report}
======================================================================
"""
    return report_text

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    explained_parquet_path = os.path.join(base_dir, "data", "dev", "entities_explained.parquet")
    ground_truth_path = os.path.join(base_dir, "data", "dev", "ground_truth.parquet")
    output_dir = os.path.join(base_dir, "outputs", "evaluation")
    output_path = os.path.join(output_dir, "model_evaluation_report.txt")
    
    if not os.path.exists(explained_parquet_path):
        print(f"Error: Parquet file not found at {explained_parquet_path}. Run explain_risk.py first.")
        sys.exit(1)
    if not os.path.exists(ground_truth_path):
        print(f"Error: Ground-truth parquet not found at {ground_truth_path}.")
        sys.exit(1)
        
    print(f"Loading explained entities from {explained_parquet_path}...")
    df = pd.read_parquet(explained_parquet_path)
    print(f"Loading wallet-level ground truth from {ground_truth_path}...")
    ground_truth = load_ground_truth(ground_truth_path)
    
    print("Computing pipeline performance evaluation...")
    report_content = generate_report(df, ground_truth)
    
    # Save report to text file
    print(f"Saving evaluation report to {output_path}...")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    # Print report to console
    print(report_content)
    print("Evaluation completed.")

if __name__ == "__main__":
    main()
