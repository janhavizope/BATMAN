"""
test_risk.py
Unit tests for the Step 5 continuous risk scoring engine.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Adjust path to find backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.core.backend.risk.risk_score import continuousRiskEngine

class TestRiskScore(unittest.TestCase):
    def setUp(self):
        # Create a small dataset with 3 entities
        # entity_0 is normal
        # entity_1 is an outlier (cluster -1) but moderate anomaly score
        # entity_2 has maximum anomaly score and no cluster boost
        self.mock_data = {
            "anomaly_score": [-1.0, 0.0, 1.0],
            "cluster_label": [0, -1, 1]
        }
        self.df = pd.DataFrame(self.mock_data)
        self.df.index = [f"wallet_{i}" for i in range(3)]
        
    def test_risk_calculations(self):
        """Test that the continuous risk scoring engine computes contributions correctly."""
        engine = continuousRiskEngine(anomaly_weight=80.0, cluster_boost=20.0)
        result_df = engine.compute_risk(self.df)
        
        # Verify columns exist
        self.assertIn("anomaly_component", result_df.columns)
        self.assertIn("cluster_component", result_df.columns)
        self.assertIn("risk_score", result_df.columns)
        
        # Min score is -1.0 (maps to 80.0 contribution, most anomalous)
        # Max score is 1.0 (maps to 0.0 contribution, least anomalous)
        # Range is 2.0. So score 0.0 maps to 0.5 * 80.0 = 40.0 contribution
        
        # wallet_0 (min anomaly score = -1.0, normal cluster)
        self.assertEqual(result_df.loc["wallet_0"]["anomaly_component"], 80.0)
        self.assertEqual(result_df.loc["wallet_0"]["cluster_component"], 0.0)
        self.assertEqual(result_df.loc["wallet_0"]["risk_score"], 80.0)
        
        # wallet_1 (middle anomaly score = 0.0, outlier cluster)
        self.assertEqual(result_df.loc["wallet_1"]["anomaly_component"], 40.0)
        self.assertEqual(result_df.loc["wallet_1"]["cluster_component"], 20.0)
        self.assertEqual(result_df.loc["wallet_1"]["risk_score"], 60.0)
        
        # wallet_2 (max anomaly score = 1.0, normal cluster)
        self.assertEqual(result_df.loc["wallet_2"]["anomaly_component"], 0.0)
        self.assertEqual(result_df.loc["wallet_2"]["cluster_component"], 0.0)
        self.assertEqual(result_df.loc["wallet_2"]["risk_score"], 0.0)

    def test_clipping_behavior(self):
        """Test that risk scores are clipped to [0, 100]."""
        # If we set high weights, they should be capped at 100
        engine = continuousRiskEngine(anomaly_weight=200.0, cluster_boost=50.0)
        result_df = engine.compute_risk(self.df)
        
        # wallet_0 has min score -> 200 contribution. Clipped to 100.
        self.assertEqual(result_df.loc["wallet_0"]["risk_score"], 100.0)

if __name__ == "__main__":
    unittest.main()
