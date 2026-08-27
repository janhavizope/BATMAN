"""
feature_engineering.py
Feature engineering module for the Bitcoin transaction monitoring backend.
Extracts transaction, wallet, temporal, graph, and network features for each unique wallet address.
"""

import os
import sys
import pandas as pd
import numpy as np
import networkx as nx
from typing import Tuple, Dict, Any

# Ensure graph builder and ingestor can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.graph.graph_builder import TransactionGraphBuilder

class WalletFeatureEngineer:
    """
    Engineers a set of numeric features for each wallet address.
    Excludes ground-truth features (is_suspicious, pattern_type) for evaluation only.
    """
    
    def __init__(self):
        self.graph_builder = TransactionGraphBuilder()

    def engineer_features(self, df: pd.DataFrame, G: nx.DiGraph = None) -> pd.DataFrame:
        """
        Processes transaction data to construct wallet features.
        
        Args:
            df: Validated transaction DataFrame.
            G: NetworkX directed heterogeneous graph.
            
        Returns:
            pandas DataFrame containing only the engineered features, with wallet_address as index.
        """
        if G is None:
            G = self.graph_builder.build_graph(df)

        # Identify all unique wallets
        all_wallets = set()
        for _, row in df.iterrows():
            all_wallets.update(row["input_addresses[]"])
            all_wallets.update(row["output_addresses[]"])
        all_wallets = sorted(list(all_wallets))

        # Precompute graph centrality once for the entire graph
        print("Computing betweenness centrality (exact)...")
        bc = nx.betweenness_centrality(G)

        feature_records = []

        for wallet in all_wallets:
            # Filter transactions where this wallet is an input (sender)
            inputs_df = df[df["input_addresses[]"].apply(lambda x: wallet in x)]
            # Filter transactions where this wallet is an output (receiver)
            outputs_df = df[df["output_addresses[]"].apply(lambda x: wallet in x)]
            
            # Combine all unique transactions for this wallet, sorted chronologically
            wallet_df = pd.concat([inputs_df, outputs_df]).drop_duplicates(subset=["txid"])
            wallet_df = wallet_df.sort_values(by="timestamp").reset_index(drop=True)

            if wallet_df.empty:
                continue

            # Compute specific amounts received/sent by this wallet
            specific_amounts_received = []
            for _, row in outputs_df.iterrows():
                try:
                    idx = row["output_addresses[]"].index(wallet)
                    specific_amounts_received.append(float(row["output_amounts[]"][idx]))
                except (ValueError, IndexError):
                    pass

            specific_amounts_sent = []
            for _, row in inputs_df.iterrows():
                try:
                    idx = row["input_addresses[]"].index(wallet)
                    specific_amounts_sent.append(float(row["input_amounts[]"][idx]))
                except (ValueError, IndexError):
                    pass

            # ----------------------------------------------------
            # 1. Transaction Features
            # ----------------------------------------------------
            tx_amounts = wallet_df["output_amounts[]"].apply(sum)
            avg_amount = tx_amounts.mean() if not tx_amounts.empty else 0.0
            avg_fee = wallet_df["fee"].mean() if not wallet_df["fee"].empty else 0.0
            
            avg_input_count = wallet_df["input_addresses[]"].apply(len).mean() if not wallet_df.empty else 0.0
            avg_output_count = wallet_df["output_addresses[]"].apply(len).mean() if not wallet_df.empty else 0.0

            # ----------------------------------------------------
            # 2. Wallet Features
            # ----------------------------------------------------
            total_tx = len(wallet_df)
            total_sent = sum(specific_amounts_sent)
            total_received = sum(specific_amounts_received)
            
            counterparties = set()
            for _, row in wallet_df.iterrows():
                counterparties.update(row["input_addresses[]"])
                counterparties.update(row["output_addresses[]"])
            counterparties.discard(wallet)
            unique_counterparties = len(counterparties)

            # ----------------------------------------------------
            # 3. Temporal Features
            # ----------------------------------------------------
            timestamps = pd.to_datetime(wallet_df["timestamp"])
            wallet_age = (timestamps.max() - timestamps.min()).total_seconds()
            
            age_hours = max(wallet_age / 3600.0, 1.0)
            tx_per_hour = total_tx / age_hours
            
            if len(timestamps) > 1:
                inter_arrival_times = timestamps.diff().dropna().dt.total_seconds()
                avg_inter_arrival = inter_arrival_times.mean()
                # burst: transactions occurring within 10 seconds of each other
                burst_count = int((inter_arrival_times < 10).sum())
            else:
                avg_inter_arrival = 0.0
                burst_count = 0

            # ----------------------------------------------------
            # 4. Graph Features
            # ----------------------------------------------------
            wallet_node = f"wallet:{wallet}"
            degree = G.degree(wallet_node) if wallet_node in G else 0
            in_degree = G.in_degree(wallet_node) if (wallet_node in G and hasattr(G, "in_degree")) else degree
            out_degree = G.out_degree(wallet_node) if (wallet_node in G and hasattr(G, "out_degree")) else degree
            betweenness_val = bc.get(wallet_node, 0.0)

            # ----------------------------------------------------
            # 5. Network Features
            # ----------------------------------------------------
            associated_ips = pd.concat([inputs_df["src_ip"], outputs_df["dst_ip"]]).dropna().unique()
            unique_ip_count = len(associated_ips)
            
            associated_asns = wallet_df["asn"].dropna().unique()
            unique_asn_count = len(associated_asns)
            
            associated_countries = wallet_df["geo_country"].dropna().unique()
            unique_country_count = len(associated_countries)

            feature_records.append({
                "wallet_address": wallet,
                # Transaction
                "avg_amount": avg_amount,
                "avg_fee": avg_fee,
                "avg_input_count": avg_input_count,
                "avg_output_count": avg_output_count,
                # Wallet
                "total_tx_count": total_tx,
                "total_sent": total_sent,
                "total_received": total_received,
                "unique_counterparties": unique_counterparties,
                # Temporal
                "tx_per_hour": tx_per_hour,
                "avg_inter_arrival_time": avg_inter_arrival,
                "burst_count": burst_count,
                # Graph
                "degree": degree,
                "in_degree": in_degree,
                "out_degree": out_degree,
                "betweenness_centrality": betweenness_val,
                # Network
                "unique_ip_count": unique_ip_count,
                "unique_asn_count": unique_asn_count,
                "unique_country_count": unique_country_count
            })

        features_df = pd.DataFrame(feature_records)
        if not features_df.empty:
            features_df = features_df.set_index("wallet_address")
        else:
            features_df = pd.DataFrame(columns=[
                "avg_amount", "avg_fee", "avg_input_count", "avg_output_count",
                "total_tx_count", "total_sent", "total_received", "unique_counterparties",
                "tx_per_hour", "avg_inter_arrival_time", "burst_count",
                "degree", "in_degree", "out_degree", "betweenness_centrality",
                "unique_ip_count", "unique_asn_count", "unique_country_count"
            ])
            features_df.index.name = "wallet_address"

        return features_df

if __name__ == "__main__":
    from backend.ingestion.ingestor import TransactionIngestor
    
    # Configure path references
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    dataset_path = os.path.join(base_dir, "data", "dev", "dev_dataset.csv")
    output_parquet_path = os.path.join(base_dir, "data", "dev", "features.parquet")
    
    if not os.path.exists(dataset_path):
        print(f"Error: dataset not found at {dataset_path}")
        sys.exit(1)
        
    print(f"Loading transaction dataset from {dataset_path}...")
    ingestor = TransactionIngestor()
    df, _ = ingestor.ingest(dataset_path)
    
    print("Building transaction graph...")
    graph_builder = TransactionGraphBuilder()
    G = graph_builder.build_graph(df)
    
    print("Running feature engineering...")
    engineer = WalletFeatureEngineer()
    features_df = engineer.engineer_features(df, G)
    
    # Save to parquet
    print(f"Saving features to Parquet at {output_parquet_path}...")
    os.makedirs(os.path.dirname(output_parquet_path), exist_ok=True)
    features_df.to_parquet(output_parquet_path)
    
    print("\n--- FIRST 5 ROWS ---")
    print(features_df.head(5).to_string())
    
    print("\n--- BASIC STATS (MIN, MAX, MEAN) ---")
    stats_df = pd.DataFrame({
        "min": features_df.min(),
        "max": features_df.max(),
        "mean": features_df.mean()
    })
    print(stats_df.to_string())
    
    print("\nFeature engineering execution completed.")
