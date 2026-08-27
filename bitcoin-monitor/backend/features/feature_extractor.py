"""
feature_extractor.py
Extracts behavioral, temporal, graph, and network features for each wallet address.
Generates a structured entity-level dataset for machine learning models.
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, Any, Tuple
from backend.graph.graph_builder import TransactionGraphBuilder

class WalletFeatureExtractor:
    """
    Extracts features for each unique wallet address.
    Excluded ground truth variables (is_suspicious, pattern_type) from output features.
    """
    
    def __init__(self):
        self.graph_builder = TransactionGraphBuilder()

    def _entropy(self, series: pd.Series) -> float:
        """Compute Shannon entropy (base 2) of a categorical series."""
        if series.empty:
            return 0.0
        probs = series.value_counts(normalize=True)
        return float(-np.sum(probs * np.log2(probs + 1e-12)))

    def extract_features(self, df: pd.DataFrame, G: nx.DiGraph = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Extracts features for each wallet address.
        
        Args:
            df: Ingested and validated transaction DataFrame.
            G: Heterogeneous NetworkX graph (optional, will be built if None).
            
        Returns:
            A tuple containing:
                - features_df: DataFrame where each row is a wallet, index is 'wallet_address'.
                               Does NOT contain 'is_suspicious' or 'pattern_type'.
                - ground_truth_df: DataFrame containing 'is_suspicious' and 'pattern_type' for evaluation.
        """
        if G is None:
            G = self.graph_builder.build_graph(df)

        # 1. Identify all unique wallets
        all_wallets = set()
        for _, row in df.iterrows():
            all_wallets.update(row["input_addresses[]"])
            all_wallets.update(row["output_addresses[]"])
        all_wallets = sorted(list(all_wallets))

        # Precompute graph metrics for efficiency
        print("Precomputing graph metrics (PageRank, centrality, clustering, k-core)...")
        pr = nx.pagerank(G)
        
        # Approximated betweenness centrality if graph is large, else exact
        if len(G) > 2000:
            bc = nx.betweenness_centrality(G, k=500)
        else:
            bc = nx.betweenness_centrality(G)
            
        undirected_G = G.to_undirected()
        cc = nx.clustering(undirected_G)
        core_numbers = nx.core_number(undirected_G)

        feature_records = []
        gt_records = []

        for wallet in all_wallets:
            # Filter transactions where this wallet is an input (sender)
            inputs_df = df[df["input_addresses[]"].apply(lambda x: wallet in x)]
            # Filter transactions where this wallet is an output (receiver)
            outputs_df = df[df["output_addresses[]"].apply(lambda x: wallet in x)]
            
            # Combine and sort chronologically
            wallet_df = pd.concat([inputs_df, outputs_df]).drop_duplicates(subset=["txid"])
            wallet_df = wallet_df.sort_values(by="timestamp").reset_index(drop=True)

            if wallet_df.empty:
                continue

            # Identify primary entity id (mode)
            entity_ids = wallet_df["entity_id"].dropna()
            entity_id = entity_ids.mode().iloc[0] if not entity_ids.empty else "UNKNOWN"

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

            all_specific_amounts = specific_amounts_received + specific_amounts_sent
            if not all_specific_amounts:
                all_specific_amounts = [0.0]

            # ----------------------------------------------------
            # A. Transaction Features (aggregated at wallet level)
            # ----------------------------------------------------
            tx_amounts = wallet_df["output_amounts[]"].apply(sum)
            avg_amount = tx_amounts.mean() if not tx_amounts.empty else 0.0
            avg_fee = wallet_df["fee"].mean() if not wallet_df["fee"].empty else 0.0
            
            avg_input_count = wallet_df["input_addresses[]"].apply(len).mean() if not wallet_df.empty else 0.0
            avg_output_count = wallet_df["output_addresses[]"].apply(len).mean() if not wallet_df.empty else 0.0
            
            # fee ratio: fee / (output amounts)
            fee_ratios = wallet_df.apply(lambda r: float(r["fee"]) / (sum(r["output_amounts[]"]) + 1e-12), axis=1)
            avg_fee_ratio = fee_ratios.mean()
            
            # input/output ratio in tx
            io_ratios = wallet_df.apply(lambda r: len(r["input_addresses[]"]) / (len(r["output_addresses[]"]) + 1e-12), axis=1)
            avg_io_ratio = io_ratios.mean()

            # ----------------------------------------------------
            # B. Wallet / Entity Features
            # ----------------------------------------------------
            total_tx = len(wallet_df)
            incoming_count = len(outputs_df)
            outgoing_count = len(inputs_df)
            total_received = sum(specific_amounts_received)
            total_sent = sum(specific_amounts_sent)
            
            avg_tx_amount = np.mean(all_specific_amounts)
            max_tx_amount = np.max(all_specific_amounts)
            min_tx_amount = np.min(all_specific_amounts)
            
            # Counterparties
            counterparties = set()
            for _, row in wallet_df.iterrows():
                counterparties.update(row["input_addresses[]"])
                counterparties.update(row["output_addresses[]"])
            counterparties.discard(wallet)
            unique_counterparties = len(counterparties)
            
            # Age
            timestamps = pd.to_datetime(wallet_df["timestamp"])
            wallet_age = (timestamps.max() - timestamps.min()).total_seconds()

            # ----------------------------------------------------
            # C. Temporal Features
            # ----------------------------------------------------
            # age denominators
            age_hours = max(wallet_age / 3600.0, 1.0)
            age_days = max(wallet_age / 86400.0, 1.0)
            
            tx_per_hour = total_tx / age_hours
            tx_per_day = total_tx / age_days
            tx_velocity = total_tx / max(wallet_age, 1.0)
            
            # Inter-arrival time
            if len(timestamps) > 1:
                inter_arrival_times = timestamps.diff().dropna().dt.total_seconds()
                avg_inter_arrival = inter_arrival_times.mean()
                # burst: consecutive txs occurring < 10 seconds apart
                burst_frequency = int((inter_arrival_times < 10).sum())
                # short interval: occurred < 1 minute apart
                short_interval_count = int((inter_arrival_times < 60).sum())
            else:
                avg_inter_arrival = 0.0
                burst_frequency = 0
                short_interval_count = 0

            # ----------------------------------------------------
            # D. Graph Features
            # ----------------------------------------------------
            wallet_node = f"wallet:{wallet}"
            degree = G.degree(wallet_node) if wallet_node in G else 0
            in_degree = G.in_degree(wallet_node) if (wallet_node in G and hasattr(G, "in_degree")) else degree
            out_degree = G.out_degree(wallet_node) if (wallet_node in G and hasattr(G, "out_degree")) else degree
            
            pagerank_val = pr.get(wallet_node, 0.0)
            betweenness_val = bc.get(wallet_node, 0.0)
            clustering_val = cc.get(wallet_node, 0.0)
            k_core_val = core_numbers.get(wallet_node, 0)

            # ----------------------------------------------------
            # E. Network Features
            # ----------------------------------------------------
            associated_ips = pd.concat([inputs_df["src_ip"], outputs_df["dst_ip"]]).dropna().unique()
            unique_ip_count = len(associated_ips)
            
            associated_asns = wallet_df["asn"].dropna().unique()
            unique_asn_count = len(associated_asns)
            
            associated_countries = wallet_df["geo_country"].dropna()
            unique_country_count = associated_countries.nunique()
            
            ip_change_frequency = unique_ip_count / total_tx
            
            # Peer count (wallets connected at distance 2 in graph)
            peer_wallets = self.graph_builder.find_connected_wallets(G, wallet, max_hops=2)
            peer_count = len(peer_wallets)
            
            # Port distribution
            dest_ports = wallet_df["dst_port"].dropna()
            dest_port_diversity = dest_ports.nunique()
            
            # Network diversity (entropy of country distribution)
            network_diversity = self._entropy(associated_countries)

            # Compile feature record
            feature_records.append({
                "wallet_address": wallet,
                "entity_id": entity_id,
                # Transaction
                "tx_amount_avg": avg_amount,
                "tx_fee_avg": avg_fee,
                "avg_input_count": avg_input_count,
                "avg_output_count": avg_output_count,
                "fee_ratio": avg_fee_ratio,
                "input_output_ratio": avg_io_ratio,
                # Wallet
                "total_tx_count": total_tx,
                "incoming_count": incoming_count,
                "outgoing_count": outgoing_count,
                "total_received": total_received,
                "total_sent": total_sent,
                "avg_tx_amount": avg_tx_amount,
                "max_tx_amount": max_tx_amount,
                "min_tx_amount": min_tx_amount,
                "unique_counterparties": unique_counterparties,
                "wallet_age": wallet_age,
                # Temporal
                "tx_per_hour": tx_per_hour,
                "tx_per_day": tx_per_day,
                "tx_velocity": tx_velocity,
                "avg_inter_arrival_time": avg_inter_arrival,
                "burst_frequency": burst_frequency,
                "short_interval_transaction_count": short_interval_count,
                # Graph
                "degree": degree,
                "in_degree": in_degree,
                "out_degree": out_degree,
                "pagerank": pagerank_val,
                "betweenness_centrality": betweenness_val,
                "clustering_coefficient": clustering_val,
                "k_core": k_core_val,
                # Network
                "unique_ip_count": unique_ip_count,
                "unique_asn_count": unique_asn_count,
                "unique_country_count": unique_country_count,
                "ip_change_frequency": ip_change_frequency,
                "peer_count": peer_count,
                "destination_port_dist": dest_port_diversity,
                "network_diversity": network_diversity
            })

            # Compile ground truth record (contains labels for evaluation only)
            is_suspicious = bool(wallet_df["is_suspicious"].any())
            
            # Find the most frequent pattern type among suspicious transactions, or 'normal'
            suspicious_txs = wallet_df[wallet_df["is_suspicious"] == True]
            if not suspicious_txs.empty:
                pattern_type = suspicious_txs["pattern_type"].mode().iloc[0]
            else:
                pattern_type = "normal"
                
            gt_records.append({
                "wallet_address": wallet,
                "entity_id": entity_id,
                "is_suspicious": is_suspicious,
                "pattern_type": pattern_type
            })

        features_df = pd.DataFrame(feature_records).set_index("wallet_address")
        ground_truth_df = pd.DataFrame(gt_records).set_index("wallet_address")

        return features_df, ground_truth_df
