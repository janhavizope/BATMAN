#!/usr/bin/env python3
"""
run_step2.py
Driver script to run correlation and graph construction on data/dev/dev_dataset.csv,
print basic network statistics, test multi-hop traversal, and save the degree distribution.
"""

import os
import sys
import collections
import pandas as pd
import numpy as np

# Set matplotlib backend for headless execution
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Adjust module path to find backend packages
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.core.backend.ingestion.ingestor import TransactionIngestor
from src.core.backend.correlation.correlator import TransactionCorrelator
from src.core.backend.graph.graph_builder import TransactionGraphBuilder

def main():
    dataset_path = os.path.join("data", "dev", "dev_dataset.csv")
    if not os.path.exists(dataset_path):
        # Check parent folder relative path if executed inside scripts/
        dataset_path = os.path.join("..", "data", "dev", "dev_dataset.csv")
        
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}. Please run generate_dev_data.py first.")
        sys.exit(1)

    print(f"Loading data from {dataset_path}...")
    ingestor = TransactionIngestor()
    df, ingest_report = ingestor.ingest(dataset_path)
    
    print("\n================ CORRELATION ================ ")
    print("Correlating wallet, IP, ASN, and country associations...")
    correlator = TransactionCorrelator()
    correlations = correlator.correlate(df)
    
    wallet_net = correlations["wallet_network"]
    ip_tx = correlations["ip_transaction"]
    
    print(f"Wallet-Network Association entries generated: {len(wallet_net)}")
    print(f"IP-Transaction Association entries generated: {len(ip_tx)}")
    
    print("\nTop 5 Wallet Network Associations by Transaction Frequency:")
    print(wallet_net.head(5).to_string(index=False))
    
    print("\n================ GRAPH CONSTRUCTION ================ ")
    print("Building heterogeneous NetworkX graph...")
    graph_builder = TransactionGraphBuilder()
    G = graph_builder.build_graph(df)
    
    # Calculate stats
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    
    print(f"Nodes in Graph: {num_nodes}")
    print(f"Edges in Graph: {num_edges}")
    
    # Node types count
    node_types = collections.Counter(nx_attr.get("type", "unknown") for _, nx_attr in G.nodes(data=True))
    print("\nNode Counts by Type:")
    for ntype, count in node_types.items():
        print(f"  - {ntype}: {count}")
        
    # Degree statistics
    degrees = [d for _, d in G.degree()]
    print("\nGraph Degree Statistics:")
    print(f"  - Min Degree: {np.min(degrees)}")
    print(f"  - Max Degree: {np.max(degrees)}")
    print(f"  - Average Degree: {np.mean(degrees):.4f}")
    
    # Multi-hop traversal test
    # Find a sample wallet to start with
    wallets = [n for n, attr in G.nodes(data=True) if attr.get("type") == "wallet"]
    if wallets:
        sample_wallet_node = wallets[0]
        sample_wallet = sample_wallet_node.split(":", 1)[1]
        print(f"\nTesting Multi-hop traversal from wallet: {sample_wallet}")
        
        # Traversing 2 hops (find direct counterparty wallets via transactions/IPs)
        connected_wallets = graph_builder.find_connected_wallets(G, sample_wallet, max_hops=2)
        print(f"  - Wallets found within 2 hops: {len(connected_wallets)}")
        
        # Display first 5 connected wallets
        for w, dist in list(connected_wallets.items())[:5]:
            print(f"    * {w} (distance: {dist} hops)")
            
        # Traversing 4 hops (indirect counterparty connections)
        connected_wallets_4 = graph_builder.find_connected_wallets(G, sample_wallet, max_hops=4)
        print(f"  - Wallets found within 4 hops: {len(connected_wallets_4)}")
        
    # Plot and save degree distribution
    print("\nPlotting degree distribution...")
    plt.figure(figsize=(8, 5))
    plt.hist(degrees, bins=range(1, max(degrees) + 2), color="skyblue", edgecolor="black", alpha=0.7)
    plt.title("Heterogeneous Graph Node Degree Distribution")
    plt.xlabel("Degree")
    plt.ylabel("Node Count (Log Scale)" if num_nodes > 100 else "Node Count")
    plt.yscale("log" if num_nodes > 100 else "linear")
    plt.grid(axis='y', alpha=0.3)
    
    # Output path
    output_dir = os.path.dirname(dataset_path)
    plot_path = os.path.join(output_dir, "degree_distribution.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()
    
    print(f"Saved degree distribution plot to: {plot_path}")
    print("Step 2 Pipeline Run Done.")

if __name__ == "__main__":
    main()
