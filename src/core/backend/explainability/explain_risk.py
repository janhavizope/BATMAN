"""
explain_risk.py
Explainability module for Bitcoin transaction monitoring risk.
Uses statistical z-scores to identify the top features that contributed most to 
each entity's anomaly status, formatting them into human-readable explanations.
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import List

# Ensure backend packages can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

class RiskExplainer:
    """
    Identifies and formats features contributing most to an entity's anomaly classification.
    """
    
    def __init__(self):
        pass

    def generate_explanations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates human-readable explanations for all entities.
        
        Z-Score Explanation:
        - Z-Score: z = (value - mean) / std
          It measures how many standard deviations an entity's feature value is from 
          the average behavior of the entire population.
        - Absolute Z-Score: |z|
          The features with the largest absolute z-scores are those where the entity 
          deviates most from the norm. These represent the primary drivers of 
          unsupervised isolation/anomaly detection.
        """
        working_df = df.copy()
        
        # Define behavioral features (exclude metadata and scores)
        exclude_cols = [
            "entity_id", "risk_flag", "risk_reason", "anomaly_score", 
            "cluster_label", "anomaly_component", "cluster_component", "risk_score"
        ]
        feature_cols = [c for c in working_df.columns if c not in exclude_cols]
        
        # Calculate dataset mean and std for features
        means = working_df[feature_cols].mean()
        stds = working_df[feature_cols].std()
        
        # Replace 0 std with epsilon to avoid division by zero
        stds = stds.replace(0.0, 1e-12)
        
        explanations = []
        
        for idx, row in working_df.iterrows():
            z_scores = {}
            for col in feature_cols:
                val = row[col]
                mean = means[col]
                std = stds[col]
                # Calculate z-score
                z = (val - mean) / std
                z_scores[col] = (z, val, mean)
                
            # Sort by absolute z-score descending to find the top 3 anomalies
            sorted_features = sorted(
                z_scores.items(), 
                key=lambda item: abs(item[1][0]), 
                reverse=True
            )[:3]
            
            # Construct human-readable string parts
            parts = []
            for col, (z, val, mean) in sorted_features:
                # Clean up feature name for display
                clean_name = col.replace("_", " ")
                
                # Determine High/Low direction
                direction = "High" if z > 0 else "Low"
                
                # Calculate ratio to average
                if abs(mean) > 1e-5:
                    ratio = val / mean
                    ratio_str = f"{ratio:.1f}x avg"
                else:
                    ratio_str = f"{val:.2f} vs {mean:.2f} avg"
                    
                parts.append(f"{direction} {clean_name} ({ratio_str})")
                
            explanation_str = ", ".join(parts)
            explanations.append(explanation_str)
            
        working_df["explanation"] = explanations
        return working_df

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    risk_parquet_path = os.path.join(base_dir, "data", "dev", "entities_with_risk_score.parquet")
    output_path = os.path.join(base_dir, "data", "dev", "entities_explained.parquet")
    
    if not os.path.exists(risk_parquet_path):
        print(f"Error: Parquet file not found at {risk_parquet_path}. Run risk scoring first.")
        sys.exit(1)
        
    print(f"Loading risk score dataset from {risk_parquet_path}...")
    df = pd.read_parquet(risk_parquet_path)
    
    print("Generating statistical anomaly explanations...")
    explainer = RiskExplainer()
    result_df = explainer.generate_explanations(df)
    
    # Save the output containing all previous columns + explanation
    print(f"Saving explained dataset to Parquet at {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df.to_parquet(output_path)
    
    # Print the top 10 highest risk score explanations
    print("\n--- EXPLANATIONS FOR THE TOP 10 HIGHEST RISK ENTITIES ---")
    top_10 = result_df.sort_values(by="risk_score", ascending=False).head(10)
    
    for idx, row in top_10.iterrows():
        print(f"\nWallet: {idx}")
        print(f"  Entity ID  : {row['entity_id']}")
        print(f"  Risk Score : {row['risk_score']:.2f} ({row['risk_flag']})")
        print(f"  Explanation: {row['explanation']}")
        
    print("\nExplainability pipeline completed.")

if __name__ == "__main__":
    main()
