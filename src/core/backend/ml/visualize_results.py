"""
visualize_results.py
Generates presentation-ready PNG visualizations for anomaly detection and clustering.
Saves outputs to the outputs/charts/ directory.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Set matplotlib backend to Agg to run headlessly without screen/GUI displays
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure backend packages can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    clustered_path = os.path.join(base_dir, "data", "dev", "clustered_entities.parquet")
    charts_dir = os.path.join(base_dir, "outputs", "charts")
    
    if not os.path.exists(clustered_path):
        print(f"Error: clustered_entities.parquet not found at {clustered_path}. Run clustering first.")
        sys.exit(1)
        
    print(f"Loading clustered entities from {clustered_path}...")
    df = pd.read_parquet(clustered_path)
    
    # Create outputs/charts/ directory
    os.makedirs(charts_dir, exist_ok=True)
    
    # Set seaborn style for clean, presentation-ready aesthetics
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 11, 'axes.labelsize': 12, 'axes.titlesize': 14})
    
    # ----------------------------------------------------
    # Chart 1: Histogram of Anomaly Score Distribution
    # ----------------------------------------------------
    print("Generating anomaly score distribution histogram...")
    plt.figure(figsize=(9, 5.5))
    
    # Calculate threshold for the top 10 most anomalous (lower = more anomalous)
    top_10_scores = df["anomaly_score"].sort_values(ascending=True).head(10)
    threshold = float(top_10_scores.max())
    
    # Plot histogram with Kernel Density Estimate (KDE)
    sns.histplot(df["anomaly_score"], kde=True, color="#2b5c8f", bins=30, alpha=0.7)
    
    # Vertical line marking top 10 threshold
    plt.axvline(threshold, color="#d9534f", linestyle="--", linewidth=2, 
                label=f"Top 10 Threshold ({threshold:.4f})")
    
    plt.title("Distribution of Entity Anomaly Scores (Isolation Forest)")
    plt.xlabel("Anomaly Score (lower = more anomalous)")
    plt.ylabel("Number of Wallets")
    plt.legend(loc="upper right")
    plt.tight_layout()
    
    chart_1_path = os.path.join(charts_dir, "anomaly_score_distribution.png")
    plt.savefig(chart_1_path, dpi=150)
    plt.close()
    print(f"Saved: {chart_1_path}")
    
    # ----------------------------------------------------
    # Chart 2: 2D Scatter Plot via PCA
    # ----------------------------------------------------
    print("Generating PCA 2D scatter plot of clusters...")
    plt.figure(figsize=(9, 6.5))
    
    # Extract feature columns (all numeric columns except anomaly_score and cluster_label)
    feature_cols = [c for c in df.columns if c not in ["anomaly_score", "cluster_label"]]
    X = df[feature_cols]
    
    # Standardize features prior to PCA
    X_scaled = StandardScaler().fit_transform(X)
    
    # PCA to 2 components
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    
    pca_df = pd.DataFrame(X_pca, columns=["PCA 1", "PCA 2"])
    pca_df["cluster_label"] = df["cluster_label"].values
    
    # Define color palette for clusters (assigning noise -1 to gray/black)
    unique_labels = sorted(list(pca_df["cluster_label"].unique()))
    
    # Assign distinct colors to clusters, and gray/black to noise (-1)
    colors = sns.color_palette("tab10", len(unique_labels))
    palette_dict = {}
    color_idx = 0
    for label in unique_labels:
        if label == -1:
            palette_dict[label] = "#333333"  # Dark gray for noise
        else:
            palette_dict[label] = colors[color_idx]
            color_idx += 1
            
    # Scatter plot
    sns.scatterplot(
        x="PCA 1", y="PCA 2", hue="cluster_label", 
        data=pca_df, palette=palette_dict, s=70, alpha=0.8,
        edgecolor="w", linewidth=0.5
    )
    
    # Explain variance ratios in the axes labels
    var_exp = pca.explained_variance_ratio_
    plt.title("PCA Dimensionality Reduction of Wallet Behavior Clusters")
    plt.xlabel(f"PCA Component 1 ({var_exp[0]*100:.1f}% Variance)")
    plt.ylabel(f"PCA Component 2 ({var_exp[1]*100:.1f}% Variance)")
    plt.legend(title="Cluster Label", bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    
    chart_2_path = os.path.join(charts_dir, "cluster_scatter_pca.png")
    plt.savefig(chart_2_path, dpi=150)
    plt.close()
    print(f"Saved: {chart_2_path}")
    
    # ----------------------------------------------------
    # Chart 3: Entity Count per Cluster
    # ----------------------------------------------------
    print("Generating cluster sizes bar chart...")
    plt.figure(figsize=(8, 5))
    
    cluster_counts = df["cluster_label"].value_counts().sort_index()
    
    # Convert index and values for seaborn plotting
    counts_df = pd.DataFrame({
        "Cluster": [f"Noise ({c})" if c == -1 else f"Cluster {c}" for c in cluster_counts.index],
        "Count": cluster_counts.values
    })
    
    # Set distinct color for noise versus valid clusters
    bar_colors = ["#d9534f" if "Noise" in label else "#428bca" for label in counts_df["Cluster"]]
    
    ax = sns.barplot(x="Cluster", y="Count", data=counts_df, palette=bar_colors, hue="Cluster", legend=False)
    
    # Add count labels on top of each bar
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 7), 
                    textcoords='offset points', fontweight='bold')
                    
    plt.title("Entity Frequency Distribution across Clusters")
    plt.xlabel("Cluster Group")
    plt.ylabel("Number of Wallets")
    # Increase y-limit to prevent text clipping
    plt.ylim(0, counts_df["Count"].max() * 1.15)
    plt.tight_layout()
    
    chart_3_path = os.path.join(charts_dir, "cluster_sizes.png")
    plt.savefig(chart_3_path, dpi=150)
    plt.close()
    print(f"Saved: {chart_3_path}")
    
    # ----------------------------------------------------
    # Chart 4: Top 10 Anomalous Entities Horizontal Bar Chart
    # ----------------------------------------------------
    print("Generating top 10 anomalous entities horizontal bar chart...")
    plt.figure(figsize=(9, 5.5))
    
    top_10_df = df.sort_values(by="anomaly_score", ascending=True).head(10).copy()
    # Format labels to be readable (first 6 and last 4 characters if very long)
    formatted_labels = []
    for addr in top_10_df.index:
        if len(addr) > 20:
            formatted_labels.append(f"{addr[:8]}...{addr[-8:]}")
        else:
            formatted_labels.append(addr)
            
    # Horizontal bar plot
    ax = sns.barplot(
        x="anomaly_score", y=formatted_labels, 
        data=top_10_df, palette="Reds", hue=formatted_labels, legend=False
    )
    
    # Add value annotations inside/beside the bars (handling negative widths)
    for p in ax.patches:
        width = p.get_width()
        ha = "right" if width < 0 else "left"
        offset = -5 if width < 0 else 5
        ax.annotate(f"{width:.4f}", 
                    (width, p.get_y() + p.get_height() / 2.), 
                    ha=ha, va="center", xytext=(offset, 0), 
                    textcoords="offset points", fontweight="bold")
                    
    plt.title("Top 10 Most Anomalous Entities")
    plt.xlabel("Anomaly Score (lower = more anomalous)")
    plt.ylabel("Wallet Address")
    # Leave room for annotations on the left for negative scores
    plt.xlim(top_10_df["anomaly_score"].min() * 1.15, max(0.01, top_10_df["anomaly_score"].max() * 1.15))
    plt.tight_layout()
    
    chart_4_path = os.path.join(charts_dir, "top10_anomalous_entities.png")
    plt.savefig(chart_4_path, dpi=150)
    plt.close()
    print(f"Saved: {chart_4_path}")
    
    # ----------------------------------------------------
    # Chart 5: Average Anomaly Score by Cluster Group
    # ----------------------------------------------------
    print("Generating average anomaly score by cluster group chart...")
    plt.figure(figsize=(8, 5))
    
    # Group by cluster and compute average score
    cluster_scores = df.groupby("cluster_label")["anomaly_score"].mean().sort_index()
    
    scores_df = pd.DataFrame({
        "Cluster": [f"Noise ({c})" if c == -1 else f"Cluster {c}" for c in cluster_scores.index],
        "Avg Anomaly Score": cluster_scores.values
    })
    
    # Set distinct colors: highlight Noise or Cluster 1
    palette_scores = ["#d9534f" if "Noise" in label else "#5cb85c" for label in scores_df["Cluster"]]
    
    ax = sns.barplot(x="Cluster", y="Avg Anomaly Score", data=scores_df, palette=palette_scores, hue="Cluster", legend=False)
    
    # Add values on top of bars
    for p in ax.patches:
        val = p.get_height()
        ax.annotate(f"{val:.4f}", 
                    (p.get_x() + p.get_width() / 2., val), 
                    ha='center', va='center', xytext=(0, 7 if val >= 0 else -14), 
                    textcoords='offset points', fontweight='bold')
                    
    plt.title("Average Anomaly Score Comparison by Cluster Group")
    plt.xlabel("Cluster Group")
    plt.ylabel("Average Anomaly Score")
    # Set ylim with some padding
    y_min = min(scores_df["Avg Anomaly Score"].min() * 1.2, -0.05)
    y_max = max(scores_df["Avg Anomaly Score"].max() * 1.2, 0.05)
    plt.ylim(y_min, y_max)
    plt.tight_layout()
    
    chart_5_path = os.path.join(charts_dir, "anomaly_by_cluster.png")
    plt.savefig(chart_5_path, dpi=150)
    plt.close()
    print(f"Saved: {chart_5_path}")
    
    print("\nAll anomaly detection and clustering charts generated successfully.")

if __name__ == "__main__":
    main()
