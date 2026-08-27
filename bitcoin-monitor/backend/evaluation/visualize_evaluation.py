"""
visualize_evaluation.py
Generates visual evaluation charts (confusion matrix heatmap, performance metrics
bar chart, and risk flag pie chart) using matplotlib and seaborn.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

# Ensure backend packages can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    explained_parquet_path = os.path.join(base_dir, "data", "dev", "entities_explained.parquet")
    charts_dir = os.path.join(base_dir, "outputs", "charts", "evaluation")
    
    if not os.path.exists(explained_parquet_path):
        print(f"Error: Parquet file not found at {explained_parquet_path}. Run explain_risk.py first.")
        sys.exit(1)
        
    print(f"Loading explained entities from {explained_parquet_path}...")
    df = pd.read_parquet(explained_parquet_path)
    
    # ----------------------------------------------------
    # Calculate Metrics and Confusion Matrix dynamically
    # ----------------------------------------------------
    y_true = df["entity_id"].apply(lambda eid: 1 if "adversary" in str(eid) else 0).values
    y_pred = df["risk_flag"].apply(lambda flag: 1 if flag in ["HIGH", "MEDIUM"] else 0).values
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    precision = precision_score(y_true, y_pred, zero_division=0) * 100.0
    recall = recall_score(y_true, y_pred, zero_division=0) * 100.0
    f1 = f1_score(y_true, y_pred, zero_division=0) * 100.0
    
    # Ensure charts output directory exists
    os.makedirs(charts_dir, exist_ok=True)
    
    # Set seaborn style for clean, presentation-ready aesthetics
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 11, 'axes.labelsize': 12, 'axes.titlesize': 14})
    
    # ----------------------------------------------------
    # Chart 1: Confusion Matrix Heatmap
    # ----------------------------------------------------
    print("Generating confusion matrix heatmap...")
    plt.figure(figsize=(7, 5.5))
    cm_array = np.array([[tn, fp], [fn, tp]])
    
    # Heatmap using Blue palette as requested
    ax = sns.heatmap(
        cm_array, 
        annot=True, 
        fmt="d", 
        cmap="Blues", 
        xticklabels=["Predicted Normal", "Predicted Suspicious"],
        yticklabels=["Actual Normal", "Actual Suspicious"],
        cbar=True, 
        annot_kws={"size": 13, "weight": "bold"}
    )
    
    # Customize titles and labels
    plt.title("Confusion Matrix Heatmap", fontsize=14, fontweight="bold", pad=15)
    plt.ylabel("Actual Label (Ground Truth)", fontsize=12)
    plt.xlabel("Predicted Label (Risk Engine Flag)", fontsize=12)
    plt.tight_layout()
    
    cm_path = os.path.join(charts_dir, "confusion_matrix_heatmap.png")
    plt.savefig(cm_path, dpi=150)
    plt.close()
    print(f"Saved: {cm_path}")
    
    # ----------------------------------------------------
    # Chart 2: Metrics Bar Chart
    # ----------------------------------------------------
    print("Generating metrics bar chart...")
    plt.figure(figsize=(7, 5.5))
    
    metrics = {
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1
    }
    
    # Clean blue-orange color palette
    bar_colors = ["#2b5c8f", "#e67e22", "#34495e"]
    
    ax = sns.barplot(
        x=list(metrics.keys()), 
        y=list(metrics.values()), 
        palette=bar_colors
    )
    
    # Annotate percentage values on top of each bar
    for p in ax.patches:
        val = p.get_height()
        ax.annotate(f"{val:.2f}%", 
                    (p.get_x() + p.get_width() / 2., val), 
                    ha='center', va='center', xytext=(0, 8), 
                    textcoords='offset points', fontweight='bold', fontsize=11)
                    
    plt.title("Model Performance Metrics", fontsize=14, fontweight="bold", pad=15)
    plt.ylabel("Percentage (%)", fontsize=12)
    plt.xlabel("Evaluation Metric", fontsize=12)
    plt.ylim(0, 100)
    plt.tight_layout()
    
    metrics_path = os.path.join(charts_dir, "metrics_bar_chart.png")
    plt.savefig(metrics_path, dpi=150)
    plt.close()
    print(f"Saved: {metrics_path}")
    
    # ----------------------------------------------------
    # Chart 3: Risk Flag Pie Chart
    # ----------------------------------------------------
    print("Generating risk flag pie chart...")
    plt.figure(figsize=(7, 5.5))
    
    # Make sure we maintain LOW -> MEDIUM -> HIGH order
    flag_counts = df["risk_flag"].value_counts().reindex(["LOW", "MEDIUM", "HIGH"]).fillna(0)
    
    # Clean professional colors: soft blue, amber/yellow-orange, dark orange
    pie_colors = ["#3498db", "#f39c12", "#e67e22"]
    
    # Plot pie
    plt.pie(
        flag_counts.values, 
        labels=flag_counts.index, 
        autopct='%1.1f%%',
        startangle=140, 
        colors=pie_colors, 
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    
    plt.title("Distribution of Assigned Risk Flags", fontsize=14, fontweight="bold", pad=15)
    plt.legend(flag_counts.index, loc="upper right")
    plt.tight_layout()
    
    pie_path = os.path.join(charts_dir, "risk_flag_pie_chart.png")
    plt.savefig(pie_path, dpi=150)
    plt.close()
    print(f"Saved: {pie_path}")
    
    print("\nAll evaluation visualization charts generated successfully.")

if __name__ == "__main__":
    main()
