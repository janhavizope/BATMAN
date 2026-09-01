"""
visualize_evaluation.py
Generates visual evaluation charts (confusion matrix heatmap, performance metrics
bar chart, and risk flag pie chart) using matplotlib and seaborn.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure backend packages can be imported if run directly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    evaluation_path = os.path.join(base_dir, "outputs", "evaluation", "best_unsupervised_parameters.json")
    charts_dir = os.path.join(base_dir, "outputs", "charts", "evaluation")
    
    if not os.path.exists(evaluation_path):
        print(f"Error: Persisted evaluation result not found at {evaluation_path}. Run model tuning first.")
        sys.exit(1)
        
    print(f"Loading persisted evaluation result from {evaluation_path}...")
    with open(evaluation_path, "r", encoding="utf-8") as evaluation_file:
        evaluation = json.load(evaluation_file)["best"]
    
    tn, fp, fn, tp = (evaluation[key] for key in ["tn", "fp", "fn", "tp"])
    precision = evaluation["precision"] * 100.0
    recall = evaluation["recall"] * 100.0
    f1 = evaluation["f1"] * 100.0
    
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
    # Chart 3: Accuracy Graph
    # ----------------------------------------------------
    print("Generating accuracy graph...")
    accuracy = (tp + tn) / (tp + tn + fp + fn) * 100.0
    plt.figure(figsize=(7, 5.5))
    ax = sns.barplot(x=["Accuracy"], y=[accuracy], color="#2b5c8f")
    ax.annotate(
        f"{accuracy:.2f}%",
        (ax.patches[0].get_x() + ax.patches[0].get_width() / 2.0, accuracy),
        ha="center",
        va="center",
        xytext=(0, 8),
        textcoords="offset points",
        fontweight="bold",
        fontsize=11,
    )
    plt.title("ML Model Accuracy", fontsize=14, fontweight="bold", pad=15)
    plt.ylabel("Percentage (%)", fontsize=12)
    plt.xlabel("Metric", fontsize=12)
    plt.ylim(0, 100)
    plt.tight_layout()

    accuracy_path = os.path.join(os.path.dirname(charts_dir), "accuracy_graph.png")
    plt.savefig(accuracy_path, dpi=150)
    plt.close()
    print(f"Saved: {accuracy_path}")
    
    # ----------------------------------------------------
    # Chart 4: Persisted prediction distribution
    # ----------------------------------------------------
    print("Generating risk flag pie chart...")
    plt.figure(figsize=(7, 5.5))
    
    prediction_counts = pd.Series(
        [tn + fn, fp + tp],
        index=["Predicted Normal", "Predicted Suspicious"],
    )
    
    # Clean professional colors: soft blue, amber/yellow-orange, dark orange
    pie_colors = ["#3498db", "#f39c12", "#e67e22"]
    
    # Plot pie
    plt.pie(
        prediction_counts.values,
        labels=prediction_counts.index,
        autopct='%1.1f%%',
        startangle=140, 
        colors=pie_colors, 
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    
    plt.title("Distribution of Persisted Predictions", fontsize=14, fontweight="bold", pad=15)
    plt.legend(prediction_counts.index, loc="upper right")
    plt.tight_layout()
    
    pie_path = os.path.join(charts_dir, "risk_flag_pie_chart.png")
    plt.savefig(pie_path, dpi=150)
    plt.close()
    print(f"Saved: {pie_path}")
    
    print("\nAll evaluation visualization charts generated successfully.")

if __name__ == "__main__":
    main()
