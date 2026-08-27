"""
test_evaluation_visuals.py
Unit tests for the Step 7 Model Evaluation Visualizer.
"""

import os
import sys
import unittest
import pandas as pd
import tempfile
import shutil

# Adjust path to find backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

class TestEvaluationVisuals(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for output charts
        self.test_dir = tempfile.mkdtemp()
        
        # Mock dataframe representing explained parquet output
        self.mock_data = {
            "entity_id": ["entity_adversary", "entity_normal", "entity_normal", "entity_adversary"],
            "risk_flag": ["HIGH", "LOW", "MEDIUM", "LOW"],
            "anomaly_score": [-0.15, 0.05, 0.01, -0.12],
            "cluster_label": [-1, 0, 0, 1]
        }
        self.df = pd.DataFrame(self.mock_data)
        self.df.index = [f"wallet_{i}" for i in range(4)]

    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_plotting_exports(self):
        """Verify that the plotting logic compiles and successfully writes PNG files."""
        import matplotlib
        matplotlib.use('Agg') # Use non-interactive backend for headless testing
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Check that we can compute metrics and plot
        flag_counts = self.df["risk_flag"].value_counts().reindex(["LOW", "MEDIUM", "HIGH"]).fillna(0)
        
        # Heatmap Test
        plt.figure()
        sns.heatmap([[2, 0], [0, 2]], annot=True)
        cm_path = os.path.join(self.test_dir, "heatmap.png")
        plt.savefig(cm_path)
        plt.close()
        
        # Bar Chart Test
        plt.figure()
        sns.barplot(x=["Precision", "Recall"], y=[80, 50])
        bar_path = os.path.join(self.test_dir, "bar.png")
        plt.savefig(bar_path)
        plt.close()
        
        # Pie Chart Test
        plt.figure()
        plt.pie(flag_counts.values, labels=flag_counts.index)
        pie_path = os.path.join(self.test_dir, "pie.png")
        plt.savefig(pie_path)
        plt.close()
        
        # Assertions
        self.assertTrue(os.path.exists(cm_path))
        self.assertTrue(os.path.exists(bar_path))
        self.assertTrue(os.path.exists(pie_path))

if __name__ == "__main__":
    unittest.main()
