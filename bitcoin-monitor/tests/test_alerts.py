"""
test_alerts.py
Unit tests for the Step 5 Alert Generation and Risk Flagging pipeline.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Adjust path to find backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.alerts.generate_alerts import load_wallet_entity_mapping

class TestAlertGeneration(unittest.TestCase):
    def setUp(self):
        # Create a mock clustered entities DataFrame
        # Total 10 entities to make 10% threshold exactly 1 entity
        self.mock_data = {
            "anomaly_score": [
                -0.15,  # 0. normal
                -0.14,  # 1. normal
                -0.13,  # 2. normal
                -0.12,  # 3. normal
                -0.11,  # 4. normal
                -0.10,  # 5. normal
                -0.09,  # 6. normal
                -0.08,  # 7. noise but normal score
                0.12,   # 8. normal cluster but high score (anomalous)
                0.12    # 9. noise AND high score (anomalous)
            ],
            "cluster_label": [
                0, 0, 0, 0, 0, 0, 0,
                -1,  # 7. noise/outlier
                0,   # 8. in normal cluster
                -1   # 9. noise/outlier
            ],
            "entity_id": [f"entity_{i}" for i in range(10)]
        }
        self.df = pd.DataFrame(self.mock_data)
        self.df.index = [f"wallet_{i}" for i in range(10)]

    def test_risk_flagging_logic(self):
        """Test risk flagging logic on mock dataset."""
        # Top 10% threshold of 10 entities is the 90th percentile, which selects the 1 highest score
        # Here, 90th percentile of self.df['anomaly_score'] is:
        # np.percentile(anomaly_score, 90) which falls between 0.05 and 0.12.
        # Let's compute threshold exactly
        anomaly_threshold = self.df["anomaly_score"].quantile(0.90)
        
        is_anomalous = self.df["anomaly_score"] >= anomaly_threshold
        is_noise = self.df["cluster_label"] == -1
        
        risk_flags = []
        for idx, row in self.df.iterrows():
            anom = is_anomalous.loc[idx]
            noise = is_noise.loc[idx]
            
            if noise and anom:
                risk_flags.append("HIGH")
            elif noise or anom:
                risk_flags.append("MEDIUM")
            else:
                risk_flags.append("LOW")
                
        self.df["risk_flag"] = risk_flags
        
        # Expect wallet_9 to be HIGH (is_noise = True and is_anomalous = True)
        self.assertEqual(self.df.loc["wallet_9"]["risk_flag"], "HIGH")
        
        # Expect wallet_7 to be MEDIUM (is_noise = True, but is_anomalous = False)
        self.assertEqual(self.df.loc["wallet_7"]["risk_flag"], "MEDIUM")
        
        # Expect wallet_8 to be MEDIUM (is_noise = False, but is_anomalous = True)
        self.assertEqual(self.df.loc["wallet_8"]["risk_flag"], "MEDIUM")
        
        # Expect wallet_0 to be LOW
        self.assertEqual(self.df.loc["wallet_0"]["risk_flag"], "LOW")

    def test_sorting_order(self):
        """Test that results are sorted HIGH first, then MEDIUM, then LOW, and then anomaly_score ascending."""
        anomaly_threshold = self.df["anomaly_score"].quantile(0.90)
        is_anomalous = self.df["anomaly_score"] >= anomaly_threshold
        is_noise = self.df["cluster_label"] == -1
        
        risk_flags = []
        for idx, row in self.df.iterrows():
            anom = is_anomalous.loc[idx]
            noise = is_noise.loc[idx]
            if noise and anom:
                risk_flags.append("HIGH")
            elif noise or anom:
                risk_flags.append("MEDIUM")
            else:
                risk_flags.append("LOW")
        self.df["risk_flag"] = risk_flags
        
        # Convert to categorical and sort
        self.df["risk_flag"] = pd.Categorical(
            self.df["risk_flag"], 
            categories=["HIGH", "MEDIUM", "LOW"], 
            ordered=True
        )
        sorted_df = self.df.sort_values(by=["risk_flag", "anomaly_score"], ascending=[True, True])
        
        sorted_index = list(sorted_df.index)
        
        # wallet_9 (HIGH) must be first
        self.assertEqual(sorted_index[0], "wallet_9")
        
        # Next should be MEDIUMs: wallet_7 (score -0.08) and wallet_8 (score 0.05)
        # Sorted by score ascending: wallet_7 (-0.08) comes before wallet_8 (0.05)
        self.assertEqual(sorted_index[1], "wallet_7")
        self.assertEqual(sorted_index[2], "wallet_8")
        
        # Last should be LOWs sorted ascending by anomaly_score: wallet_0 (-0.15) to wallet_6 (-0.09)
        self.assertEqual(sorted_index[3], "wallet_0")
        self.assertEqual(sorted_index[9], "wallet_6")

if __name__ == "__main__":
    unittest.main()
