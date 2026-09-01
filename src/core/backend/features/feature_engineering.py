"""
feature_engineering.py
Feature engineering module for the Bitcoin transaction monitoring backend.
Extracts transaction, wallet, temporal, graph, and network features for each unique wallet address.
"""

import os
import sys
import time
from typing import Any, Dict, Iterable, List, Optional

import networkx as nx
import numpy as np
import pandas as pd

# Ensure graph builder and ingestor can be imported if run directly.
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.graph.graph_builder import TransactionGraphBuilder

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "dev",
    "dev_dataset_50k.csv",
)
WINDOW_SECONDS = 840


class WalletFeatureEngineer:
    """Engineer wallet-level behavioral and graph features from transaction data."""

    def __init__(self):
        self.graph_builder = TransactionGraphBuilder()

    @staticmethod
    def _windowed_max_count(event_times: Iterable[Any], window_seconds: int) -> float:
        """Return the maximum number of events in any rolling time window."""
        times = pd.to_datetime(list(event_times)).sort_values().tolist()
        if not times:
            return 0.0

        seconds = np.array([ts.timestamp() for ts in times], dtype=float)
        max_count = 0
        for idx, ts in enumerate(seconds):
            start = ts - window_seconds
            end = ts
            left = np.searchsorted(seconds, start, side="left")
            count = idx - left + 1
            if count > max_count:
                max_count = int(count)
        return float(max_count)

    @staticmethod
    def _min_pass_through_gap(incoming_times: Iterable[Any], outgoing_times: Iterable[Any]) -> float:
        """Return the shortest positive gap between an incoming event and the next outgoing event."""
        incoming = sorted(pd.to_datetime(list(incoming_times)).astype("int64") / 1_000_000_000)
        outgoing = sorted(pd.to_datetime(list(outgoing_times)).astype("int64") / 1_000_000_000)

        if not incoming or not outgoing:
            return 0.0

        gaps = []
        for out_ts in outgoing:
            prior_in = [ts for ts in incoming if ts <= out_ts]
            if prior_in:
                gaps.append(float(out_ts - max(prior_in)))

        return float(min(gaps)) if gaps else 0.0

    def engineer_features(self, df: pd.DataFrame, G: Optional[nx.DiGraph] = None) -> pd.DataFrame:
        """Build wallet features with graph centrality and rolling-window temporal signals."""
        if G is None:
            G = self.graph_builder.build_graph(df)

        all_wallets = set()
        for _, row in df.iterrows():
            input_wallets = row["input_addresses[]"]
            output_wallets = row["output_addresses[]"]
            if isinstance(input_wallets, list):
                all_wallets.update(input_wallets)
            if isinstance(output_wallets, list):
                all_wallets.update(output_wallets)
        all_wallets = sorted(all_wallets)

        input_rows: Dict[str, List[int]] = {wallet: [] for wallet in all_wallets}
        output_rows: Dict[str, List[int]] = {wallet: [] for wallet in all_wallets}
        for row_index, row in df.iterrows():
            for wallet in row["input_addresses[]"]:
                input_rows[wallet].append(row_index)
            for wallet in row["output_addresses[]"]:
                output_rows[wallet].append(row_index)

        degree_centrality = nx.degree_centrality(G)
        betweenness_samples = min(50, max(10, len(G) // 20))
        betweenness_centrality = nx.betweenness_centrality(G, k=betweenness_samples, seed=42)
        pagerank = nx.pagerank(G, max_iter=200)
        core_number = nx.core_number(G.to_undirected())

        feature_records: List[Dict[str, Any]] = []

        for wallet in all_wallets:
            wallet_node = f"wallet:{wallet}"
            inputs_df = df.loc[input_rows[wallet]]
            outputs_df = df.loc[output_rows[wallet]]
            wallet_df = pd.concat([inputs_df, outputs_df]).drop_duplicates(subset=["txid"])
            wallet_df = wallet_df.sort_values(by="timestamp").reset_index(drop=True)

            if wallet_df.empty:
                continue

            specific_amounts_received: List[float] = []
            for _, row in outputs_df.iterrows():
                try:
                    idx = row["output_addresses[]"].index(wallet)
                    specific_amounts_received.append(float(row["output_amounts[]"][idx]))
                except (ValueError, IndexError, TypeError):
                    pass

            specific_amounts_sent: List[float] = []
            for _, row in inputs_df.iterrows():
                try:
                    idx = row["input_addresses[]"].index(wallet)
                    specific_amounts_sent.append(float(row["input_amounts[]"][idx]))
                except (ValueError, IndexError, TypeError):
                    pass

            tx_amounts = wallet_df["output_amounts[]"].apply(sum)
            avg_amount = float(tx_amounts.mean()) if not tx_amounts.empty else 0.0
            max_transaction_amount = float(tx_amounts.max()) if not tx_amounts.empty else 0.0
            avg_fee = float(wallet_df["fee"].mean()) if "fee" in wallet_df.columns and not wallet_df["fee"].empty else 0.0

            avg_input_count = float(wallet_df["input_addresses[]"].apply(len).mean()) if not wallet_df.empty else 0.0
            avg_output_count = float(wallet_df["output_addresses[]"].apply(len).mean()) if not wallet_df.empty else 0.0

            total_tx_count = int(len(wallet_df))
            incoming_transaction_count = int(len(inputs_df))
            outgoing_transaction_count = int(len(outputs_df))
            total_sent = float(sum(specific_amounts_sent))
            total_received = float(sum(specific_amounts_received))
            incoming_outgoing_ratio = float(total_received / max(total_sent, 1e-12))

            counterparties = set()
            incoming_counterparties = set()
            outgoing_counterparties = set()
            for _, row in inputs_df.iterrows():
                incoming_counterparties.update(row["input_addresses[]"])
            for _, row in outputs_df.iterrows():
                outgoing_counterparties.update(row["output_addresses[]"])
            incoming_counterparties.discard(wallet)
            outgoing_counterparties.discard(wallet)
            for _, row in wallet_df.iterrows():
                counterparties.update(row["input_addresses[]"])
                counterparties.update(row["output_addresses[]"])
            counterparties.discard(wallet)
            unique_counterparties = int(len(counterparties))
            fan_in_behavior = float(incoming_transaction_count / max(len(incoming_counterparties), 1))
            fan_out_behavior = float(outgoing_transaction_count / max(len(outgoing_counterparties), 1))

            timestamps = pd.to_datetime(wallet_df["timestamp"]).sort_values()
            wallet_age = (timestamps.max() - timestamps.min()).total_seconds() if len(timestamps) > 1 else 0.0
            age_hours = max(wallet_age / 3600.0, 1.0)
            tx_per_hour = float(total_tx_count / age_hours)

            if len(timestamps) > 1:
                inter_arrival_times = timestamps.diff().dropna().dt.total_seconds()
                avg_inter_arrival_time = float(inter_arrival_times.mean())
                burst_count = int((inter_arrival_times < 10).sum())
            else:
                avg_inter_arrival_time = 0.0
                burst_count = 0

            incoming_times = pd.to_datetime(inputs_df["timestamp"]).sort_values()
            outgoing_times = pd.to_datetime(outputs_df["timestamp"]).sort_values()
            max_tx_in_window = self._windowed_max_count(timestamps, WINDOW_SECONDS)
            max_fan_in_window = self._windowed_max_count(incoming_times, WINDOW_SECONDS)
            max_fan_out_window = self._windowed_max_count(outgoing_times, WINDOW_SECONDS)
            min_pass_through_gap = self._min_pass_through_gap(incoming_times, outgoing_times)

            degree_value = degree_centrality.get(wallet_node, 0.0)
            betweenness_value = betweenness_centrality.get(wallet_node, 0.0)
            pagerank_value = pagerank.get(wallet_node, 0.0)
            k_core_value = core_number.get(wallet_node, 0)

            associated_ips = pd.concat([inputs_df["src_ip"], outputs_df["dst_ip"]]).dropna().unique()
            unique_ip_count = int(len(associated_ips))
            associated_asns = wallet_df["asn"].dropna().unique()
            unique_asn_count = int(len(associated_asns))
            unique_country_count = int(len(wallet_df["geo_country"].dropna().unique()))

            feature_records.append(
                {
                    "wallet_address": wallet,
                    "WINDOW_SECONDS": WINDOW_SECONDS,
                    "avg_amount": avg_amount,
                    "max_transaction_amount": max_transaction_amount,
                    "avg_fee": avg_fee,
                    "avg_input_count": avg_input_count,
                    "avg_output_count": avg_output_count,
                    "total_tx_count": total_tx_count,
                    "incoming_transaction_count": incoming_transaction_count,
                    "outgoing_transaction_count": outgoing_transaction_count,
                    "total_sent": total_sent,
                    "total_received": total_received,
                    "incoming_outgoing_ratio": incoming_outgoing_ratio,
                    "unique_counterparties": unique_counterparties,
                    "fan_in_behavior": fan_in_behavior,
                    "fan_out_behavior": fan_out_behavior,
                    "tx_per_hour": tx_per_hour,
                    "avg_inter_arrival_time": avg_inter_arrival_time,
                    "burst_count": burst_count,
                    "max_tx_in_window": max_tx_in_window,
                    "max_fan_in_window": max_fan_in_window,
                    "max_fan_out_window": max_fan_out_window,
                    "min_pass_through_gap": min_pass_through_gap,
                    "degree_centrality": degree_value,
                    "degree": G.degree(wallet_node) if wallet_node in G else 0,
                    "in_degree": G.in_degree(wallet_node) if wallet_node in G else 0,
                    "out_degree": G.out_degree(wallet_node) if wallet_node in G else 0,
                    "betweenness_centrality": betweenness_value,
                    "pagerank": pagerank_value,
                    "k_core": k_core_value,
                    "unique_ip_count": unique_ip_count,
                    "unique_asn_count": unique_asn_count,
                    "unique_country_count": unique_country_count,
                }
            )

        features_df = pd.DataFrame(feature_records)
        if features_df.empty:
            columns = [
                "wallet_address",
                "WINDOW_SECONDS",
                "avg_amount",
                "avg_fee",
                "avg_input_count",
                "avg_output_count",
                "total_tx_count",
                "total_sent",
                "total_received",
                "unique_counterparties",
                "tx_per_hour",
                "avg_inter_arrival_time",
                "burst_count",
                "max_tx_in_window",
                "max_fan_in_window",
                "max_fan_out_window",
                "min_pass_through_gap",
                "degree_centrality",
                "degree",
                "in_degree",
                "out_degree",
                "betweenness_centrality",
                "unique_ip_count",
                "unique_asn_count",
                "unique_country_count",
            ]
            features_df = pd.DataFrame(columns=columns)
            features_df = features_df.set_index("wallet_address")
            features_df.index.name = "wallet_address"
            return features_df

        features_df = features_df.set_index("wallet_address")
        return features_df


if __name__ == "__main__":
    from backend.ingestion.ingestor import TransactionIngestor

    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    dataset_path = DATASET_PATH
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

    print(f"Saving features to Parquet at {output_parquet_path}...")
    os.makedirs(os.path.dirname(output_parquet_path), exist_ok=True)
    features_df.to_parquet(output_parquet_path)

    print("\n--- FIRST 5 ROWS ---")
    print(features_df.head(5).to_string())

    print("\n--- BASIC STATS (MIN, MAX, MEAN) ---")
    stats_df = pd.DataFrame({
        "min": features_df.min(),
        "max": features_df.max(),
        "mean": features_df.mean(),
    })
    print(stats_df.to_string())

    print("\nFeature engineering execution completed.")
