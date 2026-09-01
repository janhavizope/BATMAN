"""
risk_score.py
Computes a continuous risk score (0-100 scale) for each entity,
providing a traceable breakdown of risk factors (anomaly score + cluster boost).
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure backend packages can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

class continuousRiskEngine:
    """
    Risk Engine that combines multiple indicators (anomaly score and cluster density)
    into a single continuous risk score (0-100).
    """
    
    def __init__(self, anomaly_weight: float = 80.0, cluster_boost: float = 20.0):
        self.anomaly_weight = anomaly_weight
        self.cluster_boost = cluster_boost

    def compute_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates continuous risk scores and breakdowns.
        
        Formula:
        - anomaly_component = min_max_scaled(anomaly_score) * anomaly_weight
          Note: Since higher anomaly_score in our dataset means more anomalous,
          we scale directly so higher anomaly_score yields higher risk contribution.
        - cluster_component = +cluster_boost if cluster_label == -1 (outlier), else 0
        - risk_score = anomaly_component + cluster_component (clipped to [0, 100])
        """
        working_df = df.copy()
        
        # 1. Anomaly Component Calculation
        min_score = working_df["anomaly_score"].min()
        max_score = working_df["anomaly_score"].max()
        score_range = max_score - min_score if max_score > min_score else 1e-12
        
        # Min-max scale to [0, 1] (inverted: most negative = most anomalous)
        normalized_anomaly = (max_score - working_df["anomaly_score"]) / score_range
        
        # Calculate anomaly contribution (up to anomaly_weight, default 80 points)
        anomaly_component = normalized_anomaly * self.anomaly_weight
        
        # 2. Cluster Component Calculation (up to cluster_boost, default 20 points)
        cluster_component = (working_df["cluster_label"] == -1).astype(float) * self.cluster_boost
        
        # 3. Combine and clip
        risk_score = anomaly_component + cluster_component
        risk_score = np.clip(risk_score, 0.0, 100.0)
        
        # Add columns to dataframe
        working_df["anomaly_component"] = anomaly_component
        working_df["cluster_component"] = cluster_component
        working_df["risk_score"] = risk_score
        
        return working_df

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    alerts_path = os.path.join(base_dir, "data", "dev", "investigative_alerts.parquet")
    clustered_path = os.path.join(base_dir, "data", "dev", "clustered_entities.parquet")
    output_path = os.path.join(base_dir, "data", "dev", "entities_with_risk_score.parquet")
    
    # Load input data robustly: prefer investigative_alerts (which has risk_flag),
    # fall back to clustered_entities and recalculate risk_flag if needed.
    if os.path.exists(alerts_path):
        print(f"Loading data from investigative alerts: {alerts_path}...")
        df = pd.read_parquet(alerts_path)
    elif os.path.exists(clustered_path):
        print(f"Alerts not found. Loading clustered entities: {clustered_path}...")
        df = pd.read_parquet(clustered_path)
        # Recalculate risk_flag
        anomaly_threshold = df["anomaly_score"].quantile(0.20)
        is_anomalous = df["anomaly_score"] <= anomaly_threshold
        is_noise = df["cluster_label"] == -1
        
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
    else:
        print("Error: neither alerts nor clustered entities files were found.")
        sys.exit(1)
        
    print("Computing continuous risk scores...")
    engine = continuousRiskEngine()
    result_df = engine.compute_risk(df)
    
    # Sort by risk_score descending
    result_df_sorted = result_df.sort_values(by="risk_score", ascending=False)
    
    # Save the output
    print(f"Saving risk scores to Parquet at {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df_sorted.to_parquet(output_path)
    
    # Print Summary stats
    print("\n--- RISK SCORE STATS ---")
    print(f"  - Min Risk Score: {result_df_sorted['risk_score'].min():.4f}")
    print(f"  - Max Risk Score: {result_df_sorted['risk_score'].max():.4f}")
    print(f"  - Mean Risk Score: {result_df_sorted['risk_score'].mean():.4f}")
    
    # Print top 10 entities
    print("\n--- TOP 10 HIGHEST RISK ENTITIES ---")
    top_cols = ["entity_id", "risk_flag", "anomaly_score", "cluster_label", "anomaly_component", "cluster_component", "risk_score"]
    print(result_df_sorted[top_cols].head(10).to_string())

if __name__ == "__main__":
    main()
