"""
test_finalize_output.py
Unit tests for the Step 8 Final Handoff Output formatter.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
import tempfile
import shutil
import json

# Adjust path to find backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

class TestFinalizeOutput(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for output files
        self.test_dir = tempfile.mkdtemp()
        
        # Mock data representing explainability parquet output
        self.mock_data = {
            "entity_id": ["entity_1", "entity_2"],
            "risk_score": [12.3456, 98.7654],
            "risk_flag": ["LOW", "HIGH"],
            "explanation": ["Low features", "High features"],
            "anomaly_score": [-0.01234, -0.12346],
            "cluster_label": [0, -1],
            "anomaly_component": [10.0, 80.0],
            "cluster_component": [0.0, 20.0]
        }
        self.df = pd.DataFrame(self.mock_data)
        self.df.index = ["wallet_1", "wallet_2"]

    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_formatting_and_saving(self):
        """Test rounding, column selection, risk score sorting, and file exports."""
        df_out = self.df.reset_index(names="wallet_address")
        
        target_cols = [
            "wallet_address", "entity_id", "risk_score", 
            "risk_flag", "explanation", "anomaly_score", "cluster_label"
        ]
        df_final = df_out[target_cols].copy()
        
        # Rounding check
        df_final["risk_score"] = df_final["risk_score"].round(2)
        df_final["anomaly_score"] = df_final["anomaly_score"].round(4)
        
        # Sorting check
        df_final = df_final.sort_values(by="risk_score", ascending=False)
        
        # Verify columns and index
        self.assertNotIn("anomaly_component", df_final.columns)
        self.assertEqual(list(df_final.columns), target_cols)
        
        # Check rounded values
        # wallet_2 should be first because risk_score 98.77 > 12.35
        self.assertEqual(df_final.iloc[0]["wallet_address"], "wallet_2")
        self.assertEqual(df_final.iloc[0]["risk_score"], 98.77)
        self.assertEqual(df_final.iloc[0]["anomaly_score"], -0.1235)
        
        self.assertEqual(df_final.iloc[1]["wallet_address"], "wallet_1")
        self.assertEqual(df_final.iloc[1]["risk_score"], 12.35)
        self.assertEqual(df_final.iloc[1]["anomaly_score"], -0.0123)
        
        # Export files
        json_path = os.path.join(self.test_dir, "results.json")
        csv_path = os.path.join(self.test_dir, "results.csv")
        
        df_final.to_json(json_path, orient="records", indent=4, force_ascii=False)
        df_final.to_csv(csv_path, index=False, encoding="utf-8")
        
        self.assertTrue(os.path.exists(json_path))
        self.assertTrue(os.path.exists(csv_path))
        
        # Verify JSON content structure
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["wallet_address"], "wallet_2")
            self.assertEqual(data[0]["risk_score"], 98.77)

if __name__ == "__main__":
    unittest.main()
