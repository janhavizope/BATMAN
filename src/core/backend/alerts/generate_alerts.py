"""
generate_alerts.py
Risk scoring engine that flags entities as HIGH, MEDIUM, or LOW risk
based on anomaly scores and clustering results, generating actionable alerts.
"""

import os
import sys
import json
import pandas as pd
from typing import Tuple

# Ensure backend packages can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def load_wallet_entity_mapping(csv_path: str) -> dict:
    """Helper to map wallet_address to entity_id from the original CSV dataset."""
    if not os.path.exists(csv_path):
        return {}
        
    df = pd.read_csv(csv_path)
    wallet_to_entity = {}
    for _, row in df.iterrows():
        entity = row["entity_id"]
        # Parse inputs
        try:
            inputs = json.loads(row["input_addresses[]"])
            for w in inputs:
                wallet_to_entity[w] = entity
        except (json.JSONDecodeError, TypeError):
            pass
        # Parse outputs
        try:
            outputs = json.loads(row["output_addresses[]"])
            for w in outputs:
                wallet_to_entity[w] = entity
        except (json.JSONDecodeError, TypeError):
            pass
    return wallet_to_entity

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    clustered_path = os.path.join(base_dir, "data", "dev", "clustered_entities.parquet")
    csv_path = os.path.join(base_dir, "data", "dev", "dev_dataset.csv")
    output_parquet_path = os.path.join(base_dir, "data", "dev", "investigative_alerts.parquet")
    output_csv_dir = os.path.join(base_dir, "outputs", "alerts")
    output_csv_path = os.path.join(output_csv_dir, "flagged_entities.csv")
    
    if not os.path.exists(clustered_path):
        print(f"Error: clustered_entities.parquet not found at {clustered_path}. Run clustering first.")
        sys.exit(1)
        
    print(f"Loading clustered entities from {clustered_path}...")
    df = pd.read_parquet(clustered_path)
    
    # Resolve entity_ids to include in the output CSV
    wallet_to_entity = load_wallet_entity_mapping(csv_path)
    df["entity_id"] = df.index.map(lambda w: wallet_to_entity.get(w, "UNKNOWN"))
    
    # ----------------------------------------------------
    # Flagging Logic:
    # 1. Identify the 10% most anomalous entities.
    #    Note: raw anomaly_score has lower/more negative values for anomalies.
    #    Therefore, the 10% most anomalous corresponds to the BOTTOM 10% of values (<= 10th percentile).
    # 2. Identify noise/outlier points from HDBSCAN (cluster_label == -1).
    # 3. Apply the combination rules:
    #    - HIGH: Outlier AND in the bottom 10% anomalous group.
    #    - MEDIUM: Outlier OR in the bottom 10% anomalous group (XOR - but not both).
    #    - LOW: Otherwise (normal behavior).
    # ----------------------------------------------------
    
    # 20th percentile threshold for the most anomalous 20% of entities
    anomaly_threshold = df["anomaly_score"].quantile(0.20)
    
    # Flags
    is_anomalous = df["anomaly_score"] <= anomaly_threshold
    is_noise = df["cluster_label"] == -1
    
    # Compute risk levels
    risk_flags = []
    risk_reasons = []
    
    for idx, row in df.iterrows():
        anom = is_anomalous.loc[idx]
        noise = is_noise.loc[idx]
        
        if noise and anom:
            risk_flags.append("HIGH")
            risk_reasons.append("Outlier cluster + high anomaly score")
        elif noise or anom:
            risk_flags.append("MEDIUM")
            reason = "Outlier cluster only" if noise else "High anomaly score only"
            risk_reasons.append(reason)
        else:
            risk_flags.append("LOW")
            risk_reasons.append("Normal behavior")
            
    df["risk_flag"] = risk_flags
    df["risk_reason"] = risk_reasons
    
    # Sort results: HIGH first, then MEDIUM, then LOW, then anomaly_score ascending
    df["risk_flag"] = pd.Categorical(
        df["risk_flag"], 
        categories=["HIGH", "MEDIUM", "LOW"], 
        ordered=True
    )
    df_sorted = df.sort_values(by=["risk_flag", "anomaly_score"], ascending=[True, True])
    
    # Save the full sorted dataset
    print(f"Saving full investigative alerts to Parquet at {output_parquet_path}...")
    df_sorted.to_parquet(output_parquet_path)
    
    # Save HIGH and MEDIUM flagged entities to CSV
    flagged_df = df_sorted[df_sorted["risk_flag"].isin(["HIGH", "MEDIUM"])].copy()
    flagged_df = flagged_df.reset_index() # make wallet_address a column
    
    flagged_cols = ["wallet_address", "entity_id", "risk_flag", "risk_reason", "anomaly_score", "cluster_label"]
    flagged_df_out = flagged_df[flagged_cols]
    
    print(f"Saving flagged entities CSV to {output_csv_path}...")
    os.makedirs(output_csv_dir, exist_ok=True)
    flagged_df_out.to_csv(output_csv_path, index=False)
    
    # Print Summary stats
    print("\n--- RISK LEVEL COUNT SUMMARY ---")
    print(df_sorted["risk_flag"].value_counts().to_string())
    
    # Print the flagged entities table to console
    print("\n--- FLAGGED ENTITIES (HIGH & MEDIUM) ---")
    if not flagged_df_out.empty:
        print(flagged_df_out.to_string(index=False))
    else:
        print("No high or medium flagged entities found.")

if __name__ == "__main__":
    main()
