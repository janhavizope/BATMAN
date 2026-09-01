"""
finalize_output.py
Prepares the final handoff files for downstream consumption.
This formats, rounds, and saves the risk assessment results in pretty JSON 
and CSV formats for the frontend/dashboard team (Janhavi's team).
"""

import os
import sys
import pandas as pd

# Ensure backend packages can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    explained_parquet_path = os.path.join(base_dir, "data", "dev", "entities_explained.parquet")
    output_dir = os.path.join(base_dir, "outputs", "final")
    json_output_path = os.path.join(output_dir, "ranked_results.json")
    csv_output_path = os.path.join(output_dir, "ranked_results.csv")
    
    if not os.path.exists(explained_parquet_path):
        print(f"Error: Parquet file not found at {explained_parquet_path}. Run explain_risk.py first.")
        sys.exit(1)
        
    print(f"Loading explained entities from {explained_parquet_path}...")
    df = pd.read_parquet(explained_parquet_path)
    
    # ----------------------------------------------------
    # Frontend Handoff Formatting:
    # 1. Reset index so wallet_address becomes a standard column.
    # 2. Select only the necessary columns for downstream consumers.
    # 3. Round scores to requested decimals (risk: 2, anomaly: 4).
    # 4. Sort descending by risk_score.
    # ----------------------------------------------------
    
    # Convert index 'wallet_address' to a column
    df_out = df.reset_index(names="wallet_address")
    
    # Select columns
    target_cols = [
        "wallet_address",
        "entity_id",
        "risk_score",
        "risk_flag",
        "explanation",
        "anomaly_score",
        "cluster_label"
    ]
    
    # Ensure all target columns exist
    missing_cols = [c for c in target_cols if c not in df_out.columns]
    if missing_cols:
        print(f"Error: Missing columns in source parquet: {missing_cols}")
        sys.exit(1)
        
    df_final = df_out[target_cols].copy()
    
    # Round metrics for presentation
    df_final["risk_score"] = df_final["risk_score"].round(2)
    df_final["anomaly_score"] = df_final["anomaly_score"].round(4)
    
    # Sort by risk_score descending
    df_final = df_final.sort_values(by="risk_score", ascending=False)
    
    # Save Outputs
    print(f"Creating outputs directory: {output_dir}...")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. JSON output (list of records, pretty-printed, UTF-8)
    print(f"Saving pretty-printed JSON to {json_output_path}...")
    df_final.to_json(
        json_output_path, 
        orient="records", 
        indent=4, 
        force_ascii=False
    )
    
    # 2. CSV output (UTF-8, without indices)
    print(f"Saving CSV to {csv_output_path}...")
    df_final.to_csv(csv_output_path, index=False, encoding="utf-8")
    
    # Print handoff details
    total_records = len(df_final)
    print(f"\nSuccessfully finalized output.")
    print(f"Total Records Saved  : {total_records}")
    print(f"JSON File Location   : {json_output_path}")
    print(f"CSV File Location    : {csv_output_path}")
    print("\nHandoff files ready for frontend dashboard integration.")

if __name__ == "__main__":
    main()
