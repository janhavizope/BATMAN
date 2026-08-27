#!/usr/bin/env python3
"""
run_step3.py
Driver script to run feature engineering on data/dev/dev_dataset.csv,
print summary statistics (ranges, nulls, correlations), and save features to features.parquet.
"""

import os
import sys
import pandas as pd
import numpy as np

# Adjust module path to find backend packages
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.ingestion.ingestor import TransactionIngestor
from backend.graph.graph_builder import TransactionGraphBuilder
from backend.features.feature_engineering import WalletFeatureEngineer

def main():
    dataset_path = os.path.join("data", "dev", "dev_dataset.csv")
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join("..", "data", "dev", "dev_dataset.csv")
        
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}. Please run generate_dev_data.py first.")
        sys.exit(1)

    print(f"Loading data from {dataset_path}...")
    ingestor = TransactionIngestor()
    df, _ = ingestor.ingest(dataset_path)
    
    print("Building heterogeneous graph...")
    graph_builder = TransactionGraphBuilder()
    G = graph_builder.build_graph(df)
    
    print("Running feature engineering pipeline...")
    engineer = WalletFeatureEngineer()
    features_df = engineer.engineer_features(df, G)
    
    # Verify shape
    print(f"\nFeature Table Generated: {features_df.shape[0]} entities (wallets), {features_df.shape[1]} features.")
    
    # Assert Ground Truth is NOT in features_df
    for gt_col in ["is_suspicious", "pattern_type"]:
        assert gt_col not in features_df.columns, f"CRITICAL: {gt_col} must not be in the features dataset!"
    print("Verification passed: Ground-truth columns are excluded from features.")
    
    # Save output to features.parquet
    output_dir = os.path.dirname(dataset_path)
    output_parquet_path = os.path.join(output_dir, "features.parquet")
    features_df.to_parquet(output_parquet_path)
    print(f"Saved features Parquet to: {output_parquet_path}")

    # Print first 5 rows
    print("\n--- FIRST 5 ROWS ---")
    print(features_df.head(5).to_string())

    # Print Null / Missing count
    nulls = features_df.isnull().sum()
    print(f"\nMissing values per feature (total nulls: {nulls.sum()}):")
    if nulls.sum() > 0:
        print(nulls[nulls > 0])
    else:
        print("  - No missing values found in the engineered features.")
        
    # Print Feature Ranges (Min, Max, Mean)
    print("\n--- BASIC STATS (MIN, MAX, MEAN) ---")
    stats_df = pd.DataFrame({
        "min": features_df.min(),
        "max": features_df.max(),
        "mean": features_df.mean()
    })
    print(stats_df.to_string())
    
    # Print key feature correlations
    print("\nKey Feature Correlation Matrix (Pearson):")
    correlation_cols = ["degree", "total_tx_count", "total_received", "unique_ip_count", "betweenness_centrality"]
    correlation_cols = [c for c in correlation_cols if c in features_df.columns]
    
    corr_matrix = features_df[correlation_cols].corr()
    print(corr_matrix.round(4).to_string())
    
    print("Step 3 Pipeline Run Done.")

if __name__ == "__main__":
    main()
