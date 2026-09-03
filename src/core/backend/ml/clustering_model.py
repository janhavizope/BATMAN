"""
clustering_model.py
Clusters wallet entities using HDBSCAN on engineered numeric features.
"""

import os
import sys
from pathlib import Path

import hdbscan
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Allow the script to be run directly from the repository root.
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(REPO_ROOT))


def main() -> None:
    """Load engineered features, assign HDBSCAN clusters, and save the results."""
    REPO_ROOT = Path(__file__).resolve().parents[4]
    features_path = str(REPO_ROOT / "data" / "dev" / "features.parquet")
    output_path = str(REPO_ROOT / "data" / "dev" / "cluster_labels.parquet")

    if not os.path.exists(features_path):
        print(
            f"Error: features.parquet not found at {features_path}. "
            "Run feature engineering first."
        )
        sys.exit(1)

    print(f"Loading features from {features_path}...")
    features_df = pd.read_parquet(features_path)

    # HDBSCAN should receive only numeric engineered features.
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    X = features_df[numeric_cols]
    X_scaled = StandardScaler().fit_transform(X)

    print("Training HDBSCAN (min_cluster_size=5, min_samples=3)...")
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=3)

    # fit_predict() learns the density-based clusters and assigns one label
    # to each entity; HDBSCAN uses -1 for points classified as noise.
    cluster_ids = clusterer.fit_predict(X_scaled)

    result_df = features_df.copy()
    result_df["cluster_id"] = cluster_ids

    print(f"Saving cluster labels to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df.to_parquet(output_path)

    cluster_counts = result_df["cluster_id"].value_counts().sort_index()
    print("\n--- CLUSTER COUNTS ---")
    for cluster_id, entity_count in cluster_counts.items():
        print(f"Cluster {cluster_id}: {entity_count} entities")
    print(f"Outliers (-1): {int((cluster_ids == -1).sum())} entities")


if __name__ == "__main__":
    main()
