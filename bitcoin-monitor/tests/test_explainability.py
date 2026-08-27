"""
test_explainability.py
Unit tests for the Step 6 Risk Explainability pipeline.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Adjust path to find backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.explainability.explain_risk import RiskExplainer

class TestRiskExplainer(unittest.TestCase):
    def setUp(self):
        # Create a mock dataframe of 5 entities and 3 features
        # wallet_4 will be set as an outlier for feature_0 and feature_1
        self.mock_data = {
            "feature_0": [1.0, 1.1, 0.9, 1.0, 10.0],  # wallet_4 is high outlier
            "feature_1": [2.0, 2.1, 1.9, 2.0, 0.1],   # wallet_4 is low outlier
            "feature_2": [5.0, 5.0, 5.1, 4.9, 5.0],   # wallet_4 is normal
            "anomaly_score": [-0.1, -0.1, -0.1, -0.1, 0.15],
            "cluster_label": [0, 0, 0, 0, -1],
            "risk_score": [10.0, 11.0, 9.0, 10.0, 95.0],
            "entity_id": [f"entity_{i}" for i in range(5)]
        }
        self.df = pd.DataFrame(self.mock_data)
        self.df.index = [f"wallet_{i}" for i in range(5)]

    def test_explanation_generation(self):
        """Test that explanations contain the correct direction and relative ratio."""
        explainer = RiskExplainer()
        result_df = explainer.generate_explanations(self.df)
        
        # Verify column exists
        self.assertIn("explanation", result_df.columns)
        
        explanation_w4 = result_df.loc["wallet_4"]["explanation"]
        
        # wallet_4 has:
        # feature_0 = 10.0 (dataset mean is 2.8, std is 4.0. Z-score is 1.8)
        # feature_1 = 0.1 (dataset mean is 1.62, std is 0.85. Z-score is -1.78)
        # feature_2 = 5.0 (dataset mean is 5.0, std is 0.07. Z-score is 0)
        # So top features contributing to anomaly are feature_0 (High) and feature_1 (Low).
        
        self.assertIn("High feature 0", explanation_w4)
        self.assertIn("Low feature 1", explanation_w4)
        
        # Verify ratio formatting
        # Mean of feature_0 is 2.8. wallet_4 value is 10.0. Ratio is 10 / 2.8 = 3.6x avg.
        self.assertIn("3.6x avg", explanation_w4)
        
        # Mean of feature_1 is 1.62. wallet_4 value is 0.1. Ratio is 0.1 / 1.62 = 0.1x avg.
        self.assertIn("0.1x avg", explanation_w4)

if __name__ == "__main__":
    unittest.main()
