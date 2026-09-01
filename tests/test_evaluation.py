"""
test_evaluation.py
Unit tests for the Step 7 Model Evaluation pipeline.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Adjust path to find backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.core.backend.evaluation.evaluate_model import generate_report

class TestModelEvaluation(unittest.TestCase):
    def setUp(self):
        # Create a small dataset with known labels
        # 4 actual adversaries, 6 normal
        # System flags 3 entities as HIGH/MEDIUM, 7 as LOW
        self.mock_data = {
            "entity_id": [
                "entity_fan_in_adversary",     # 0. Actual Suspicious
                "entity_fan_out_adversary",    # 1. Actual Suspicious
                "entity_rapid_chain_adversary",# 2. Actual Suspicious
                "entity_normal_1",             # 3. Actual Normal
                "entity_normal_2",             # 4. Actual Normal
                "entity_normal_3",             # 5. Actual Normal
                "entity_normal_4",             # 6. Actual Normal
                "entity_normal_5",             # 7. Actual Normal
                "entity_normal_6",             # 8. Actual Normal
                "entity_burst_adversary"       # 9. Actual Suspicious
            ],
            "risk_flag": [
                "HIGH",    # 0. Predicted Suspicious (TP)
                "MEDIUM",  # 1. Predicted Suspicious (TP)
                "LOW",     # 2. Predicted Normal (FN - Missed)
                "LOW",     # 3. Predicted Normal (TN)
                "LOW",     # 4. Predicted Normal (TN)
                "LOW",     # 5. Predicted Normal (TN)
                "LOW",     # 6. Predicted Normal (TN)
                "LOW",     # 7. Predicted Normal (TN)
                "MEDIUM",  # 8. Predicted Suspicious (FP - False Alarm)
                "LOW"      # 9. Predicted Normal (FN - Missed)
            ]
        }
        self.df = pd.DataFrame(self.mock_data)
        self.df.index = [f"wallet_{i}" for i in range(10)]

    def test_metrics_calculation(self):
        """Test that precision, recall, and F1 calculations match expected counts."""
        # y_true (GT):
        # Index 0, 1, 2, 9 are adversaries -> y_true = [1, 1, 1, 0, 0, 0, 0, 0, 0, 1]
        # (Total actual = 4)
        
        # y_pred (System):
        # Index 0 (HIGH), 1 (MEDIUM), 8 (MEDIUM) are predicted suspicious -> y_pred = [1, 1, 0, 0, 0, 0, 0, 0, 1, 0]
        # (Total predicted = 3)
        
        # Matches:
        # TP: Index 0, 1 (2 caught)
        # FP: Index 8 (1 false alarm)
        # FN: Index 2, 9 (2 missed)
        # TN: Index 3, 4, 5, 6, 7 (5 correctly normal)
        
        # Precision = TP / (TP + FP) = 2 / 3 = 66.67%
        # Recall = TP / (TP + FN) = 2 / 4 = 50.0%
        # F1 = 2 * (P * R) / (P + R) = 2 * (0.6667 * 0.5) / (1.1667) = 57.14%
        
        report_text = generate_report(self.df)
        
        # Assertions on text content
        self.assertIn("Precision : 0.6667", report_text)
        self.assertIn("Recall    : 0.5000", report_text)
        self.assertIn("F1-Score  : 0.5714", report_text)
        
        # Confusion matrix assertions
        self.assertIn("Correctly identified Normal wallets (True Negatives)  : 5", report_text)
        self.assertIn("False alarms raised on Normal wallets (False Positives): 1", report_text)
        self.assertIn("Missed actual threats (False Negatives)               : 2", report_text)
        self.assertIn("Correctly caught actual threats (True Positives)      : 2", report_text)

if __name__ == "__main__":
    unittest.main()
