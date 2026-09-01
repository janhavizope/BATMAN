"""
graph_builder.py
Constructs a heterogeneous NetworkX graph from Bitcoin transactions 
and network traffic metadata, and implements multi-hop wallet discovery.
"""

import os
import networkx as nx
import pandas as pd
from typing import Dict, Set, Any

# Dataset consumed by this pipeline. Edit here to switch between
# the small (dev_dataset.csv) and large (dev_dataset_50k.csv) datasets.
DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "dev", "dev_dataset_50k.csv",
)

class TransactionGraphBuilder:
    """
    Builds and manages a heterogeneous directed graph representing transaction flows
    and network associations.
    """
    
    def __init__(self):
        pass

    def build_graph(self, df: pd.DataFrame) -> nx.DiGraph:
        """
        Builds a directed heterogeneous graph from a transaction DataFrame.
        
        Node Types:
            - wallet: 'wallet:<address>'
            - transaction: 'tx:<txid>'
            - ip: 'ip:<ip_address>'
            - asn: 'asn:<asn>'
            - country: 'country:<geo_country>'
            
        Edges:
            - wallet -> transaction (inputs)
            - transaction -> wallet (outputs)
            - wallet -> ip (network association)
            - ip -> asn (network mapping)
            - ip -> country (geo mapping)
        """
        G = nx.DiGraph()
        
        if df.empty:
            return G

        for _, row in df.iterrows():
            txid = row["txid"]
            timestamp = row["timestamp"]
            fee = row["fee"]
            src_ip = row["src_ip"]
            dst_ip = row["dst_ip"]
            asn = row["asn"]
            country = row["geo_country"]
            
            inputs = row["input_addresses[]"]
            outputs = row["output_addresses[]"]
            
            # Create transaction node
            tx_node = f"tx:{txid}"
            G.add_node(tx_node, type="transaction", label=txid, fee=fee, timestamp=timestamp)
            
            # Create network nodes
            src_ip_node = f"ip:{src_ip}"
            dst_ip_node = f"ip:{dst_ip}"
            asn_node = f"asn:{asn}"
            country_node = f"country:{country}"
            
            G.add_node(src_ip_node, type="ip", label=src_ip)
            G.add_node(dst_ip_node, type="ip", label=dst_ip)
            G.add_node(asn_node, type="asn", label=asn)
            G.add_node(country_node, type="country", label=country)
            
            # Link IPs to ASN and Country
            G.add_edge(src_ip_node, asn_node, type="ip_to_asn")
            G.add_edge(src_ip_node, country_node, type="ip_to_country")
            G.add_edge(dst_ip_node, asn_node, type="ip_to_asn")
            G.add_edge(dst_ip_node, country_node, type="ip_to_country")
            
            # Process input wallets
            for wallet in inputs:
                wallet_node = f"wallet:{wallet}"
                G.add_node(wallet_node, type="wallet", label=wallet)
                # Edge: wallet -> transaction (source of funds)
                G.add_edge(wallet_node, tx_node, type="wallet_to_tx")
                # Edge: wallet -> IP (network association)
                G.add_edge(wallet_node, src_ip_node, type="wallet_to_ip")

            # Process output wallets
            for wallet in outputs:
                wallet_node = f"wallet:{wallet}"
                G.add_node(wallet_node, type="wallet", label=wallet)
                # Edge: transaction -> wallet (destination of funds)
                G.add_edge(tx_node, wallet_node, type="tx_to_wallet")
                # Edge: wallet -> IP (network association)
                G.add_edge(wallet_node, dst_ip_node, type="wallet_to_ip")
                
        return G

    def find_connected_wallets(self, G: nx.DiGraph, start_wallet: str, max_hops: int = 2) -> Dict[str, int]:
        """
        Finds all wallets connected to a given wallet within N hops.
        Traverses the graph as undirected to trace back and forth through
        transactions and IPs.
        
        Args:
            G: The heterogeneous directed graph.
            start_wallet: Raw wallet address to start search from.
            max_hops: Maximum path length in the graph.
            
        Returns:
            Dict mapping wallet address string to shortest hop distance.
        """
        start_node = f"wallet:{start_wallet}" if not start_wallet.startswith("wallet:") else start_wallet
        if start_node not in G:
            return {}

        # BFS on undirected version to follow links in both directions
        undirected_G = G.to_undirected()
        
        try:
            distances = nx.single_source_shortest_path_length(undirected_G, start_node, cutoff=max_hops)
        except nx.NetworkXError:
            return {}

        connected_wallets = {}
        for node, dist in distances.items():
            if node != start_node and G.nodes[node].get("type") == "wallet":
                # Strip prefix for clean wallet outputs
                wallet_addr = node.split(":", 1)[1]
                connected_wallets[wallet_addr] = dist
                
        return connected_wallets
