"""
test_features.py
Unit tests for the Step 3 Feature Engineering pipeline.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Adjust path to find backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.core.backend.features.feature_engineering import WalletFeatureEngineer
from src.core.backend.graph.graph_builder import TransactionGraphBuilder

class TestFeatureEngineer(unittest.TestCase):
    def setUp(self):
        self.engineer = WalletFeatureEngineer()
        self.graph_builder = TransactionGraphBuilder()
        
        # Simple transaction sequence:
        # Transaction 1: wallet_A -> wallet_B, amount = 10.0, fee = 0.5
        # Transaction 2: wallet_B -> wallet_C, amount = 9.0, fee = 0.5
        self.dummy_data = [
            {
                "txid": "tx1",
                "timestamp": "2026-08-25T12:00:00",
                "src_ip": "192.168.1.1",
                "dst_ip": "10.0.0.1",
                "src_port": 8333,
                "dst_port": 8333,
                "input_addresses[]": ["wallet_A"],
                "output_addresses[]": ["wallet_B"],
                "input_amounts[]": [10.5],
                "output_amounts[]": [10.0],
                "geo_country": "US",
                "asn": "AS100",
                "fee": 0.5,
                "script_type": "P2PKH",
                "block_height": 800000,
                "block_timestamp": "2026-08-25T12:05:00",
                "connection_duration": 1.0,
                "entity_id": "entity_1",
                "is_suspicious": False,
                "pattern_type": "normal"
            },
            {
                "txid": "tx2",
                "timestamp": "2026-08-25T12:10:00",
                "src_ip": "10.0.0.1",
                "dst_ip": "10.0.0.2",
                "src_port": 8333,
                "dst_port": 8333,
                "input_addresses[]": ["wallet_B"],
                "output_addresses[]": ["wallet_C"],
                "input_amounts[]": [9.5],
                "output_amounts[]": [9.0],
                "geo_country": "US",
                "asn": "AS100",
                "fee": 0.5,
                "script_type": "P2PKH",
                "block_height": 800001,
                "block_timestamp": "2026-08-25T12:15:00",
                "connection_duration": 1.0,
                "entity_id": "entity_1",
                "is_suspicious": True,
                "pattern_type": "rapid_transfer"
            }
        ]
        self.df = pd.DataFrame(self.dummy_data)
        self.G = self.graph_builder.build_graph(self.df)

    def test_feature_engineering_columns(self):
        """Test that the feature engineering generates all expected numeric columns."""
        features_df = self.engineer.engineer_features(self.df, self.G)
        
        # Verify indices match unique wallets
        self.assertEqual(len(features_df), 3) # A, B, C
        self.assertCountEqual(features_df.index, ["wallet_A", "wallet_B", "wallet_C"])
        
        # Check exclusion of ground truth
        self.assertNotIn("is_suspicious", features_df.columns)
        self.assertNotIn("pattern_type", features_df.columns)
        
        # Check presence of expected feature columns
        expected_columns = [
            "avg_amount", "avg_fee", "avg_input_count", "avg_output_count",
            "total_tx_count", "total_sent", "total_received", "unique_counterparties",
            "tx_per_hour", "avg_inter_arrival_time", "burst_count",
            "degree", "in_degree", "out_degree", "betweenness_centrality",
            "unique_ip_count", "unique_asn_count", "unique_country_count"
        ]
        for col in expected_columns:
            self.assertIn(col, features_df.columns)

    def test_wallet_specific_values(self):
        """Test that features compute correctly for a known wallet configuration."""
        features_df = self.engineer.engineer_features(self.df, self.G)
        
        # Wallet A: sent 10.5, received 0, in 1 transaction, outgoing
        self.assertEqual(features_df.loc["wallet_A"]["total_tx_count"], 1)
        self.assertEqual(features_df.loc["wallet_A"]["total_sent"], 10.5)
        self.assertEqual(features_df.loc["wallet_A"]["total_received"], 0.0)
        self.assertEqual(features_df.loc["wallet_A"]["unique_counterparties"], 1)
        
        # Wallet B: sent 9.5 (tx2), received 10.0 (tx1), in 2 transactions
        self.assertEqual(features_df.loc["wallet_B"]["total_tx_count"], 2)
        self.assertEqual(features_df.loc["wallet_B"]["total_sent"], 9.5)
        self.assertEqual(features_df.loc["wallet_B"]["total_received"], 10.0)
        self.assertEqual(features_df.loc["wallet_B"]["unique_counterparties"], 2) # A and C

        # Wallet C: sent 0, received 9.0 (tx2), in 1 transaction
        self.assertEqual(features_df.loc["wallet_C"]["total_tx_count"], 1)
        self.assertEqual(features_df.loc["wallet_C"]["total_sent"], 0.0)
        self.assertEqual(features_df.loc["wallet_C"]["total_received"], 9.0)

if __name__ == "__main__":
    unittest.main()
