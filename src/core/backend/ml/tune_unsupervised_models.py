"""Tune unsupervised models on the labeled 141-wallet validation dataset only."""

from __future__ import annotations

import json
import os
import sys
from itertools import product
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.features.feature_engineering import WalletFeatureEngineer
from backend.graph.graph_builder import TransactionGraphBuilder
from backend.ingestion.ingestor import TransactionIngestor
from backend.ml.hdbscan_clustering import TransactionClusteredModel

BASELINE_FEATURES = [
    "avg_amount", "avg_fee", "avg_input_count", "avg_output_count",
    "total_tx_count", "total_sent", "total_received", "unique_counterparties",
    "tx_per_hour", "avg_inter_arrival_time", "burst_count", "max_tx_in_window",
    "max_fan_in_window", "max_fan_out_window", "min_pass_through_gap",
    "degree_centrality", "degree", "in_degree", "out_degree",
    "betweenness_centrality", "unique_ip_count", "unique_asn_count",
    "unique_country_count",
]
IF_CONFIGS = list(product([100, 200, 300], [0.03, 0.05, 0.08, 0.10], ["sqrt", 0.7, 1.0]))
HDBSCAN_CONFIGS = list(product([10, 15, 20, 30], [5, 10, 15]))


def prepare_features(features: pd.DataFrame, columns: Iterable[str] | None = None) -> Tuple[pd.DataFrame, list[str]]:
    numeric = features.select_dtypes(include=[np.number]).copy()
    if columns is not None:
        numeric = numeric[[column for column in columns if column in numeric.columns]]
    numeric = numeric.replace([np.inf, -np.inf], np.nan)
    numeric = numeric.dropna(axis=1, how="all")
    numeric = numeric.fillna(numeric.median()).fillna(0.0)
    numeric = numeric.loc[:, numeric.nunique(dropna=False) > 1]

    selected = []
    for column in numeric.columns:
        if not any(abs(numeric[column].corr(numeric[kept])) >= 0.95 for kept in selected):
            selected.append(column)
    return numeric[selected], selected


def load_validation_data(base_dir: str) -> Tuple[pd.DataFrame, pd.Series]:
    raw_path = os.path.join(base_dir, "data", "dev", "dev_dataset.csv")
    truth_path = os.path.join(base_dir, "data", "dev", "ground_truth.parquet")
    ingestor = TransactionIngestor()
    transactions, _ = ingestor.ingest(raw_path)
    graph = TransactionGraphBuilder().build_graph(transactions)
    features = WalletFeatureEngineer().engineer_features(transactions, graph)
    truth = pd.read_parquet(truth_path)
    if truth.index.name == "wallet_address":
        truth = truth.reset_index()
    truth = truth.set_index("wallet_address")["is_suspicious"].astype(bool)
    common = features.index.intersection(truth.index)
    if len(common) != len(features) or len(common) != len(truth):
        raise ValueError(
            f"Validation labels do not exactly cover the validation features: "
            f"features={len(features)}, labels={len(truth)}, overlap={len(common)}"
        )
    return features.loc[common], truth.loc[common]


def score_configuration(features: pd.DataFrame, labels: pd.Series, if_config: tuple, hdbscan_config: tuple, feature_set: str) -> Dict:
    n_estimators, contamination, max_samples = if_config
    min_cluster_size, min_samples = hdbscan_config
    if max_samples == "sqrt":
        max_samples = int(np.sqrt(len(features)))
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        max_samples=max_samples,
        random_state=42,
        n_jobs=-1,
    )
    anomaly_scores = model.fit(features).decision_function(features)
    anomaly_mask = anomaly_scores <= np.quantile(anomaly_scores, 0.20)

    cluster_labels = TransactionClusteredModel(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
    ).fit_predict(features)
    noise_mask = cluster_labels == -1
    predicted = anomaly_mask | noise_mask
    tn, fp, fn, tp = confusion_matrix(labels.astype(int), predicted.astype(int), labels=[0, 1]).ravel()
    return {
        "feature_set": feature_set,
        "n_estimators": n_estimators,
        "contamination": contamination,
        "max_samples": str(max_samples),
        "min_cluster_size": min_cluster_size,
        "min_samples": min_samples,
        "precision": precision_score(labels, predicted, zero_division=0),
        "recall": recall_score(labels, predicted, zero_division=0),
        "f1": f1_score(labels, predicted, zero_division=0),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "detected_anomalies": int(anomaly_mask.sum()),
        "number_of_clusters": int(len(set(cluster_labels)) - int(-1 in cluster_labels)),
        "noise_entities": int(noise_mask.sum()),
    }


def combine_predictions(labels: pd.Series, if_config: tuple, anomaly_mask: np.ndarray,
                        hdbscan_config: tuple, cluster_labels: np.ndarray, feature_set: str) -> Dict:
    noise_mask = cluster_labels == -1
    predicted = anomaly_mask | noise_mask
    tn, fp, fn, tp = confusion_matrix(labels.astype(int), predicted.astype(int), labels=[0, 1]).ravel()
    return {
        "feature_set": feature_set,
        "n_estimators": if_config[0], "contamination": if_config[1], "max_samples": str(if_config[2]),
        "min_cluster_size": hdbscan_config[0], "min_samples": hdbscan_config[1],
        "precision": precision_score(labels, predicted, zero_division=0),
        "recall": recall_score(labels, predicted, zero_division=0),
        "f1": f1_score(labels, predicted, zero_division=0),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "detected_anomalies": int(anomaly_mask.sum()),
        "number_of_clusters": int(len(set(cluster_labels)) - int(-1 in cluster_labels)),
        "noise_entities": int(noise_mask.sum()),
    }


def main() -> None:
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    output_dir = os.path.join(base_dir, "outputs", "evaluation")
    os.makedirs(output_dir, exist_ok=True)
    features, labels = load_validation_data(base_dir)
    selected_features, selected_columns = prepare_features(features)
    baseline_features, baseline_columns = prepare_features(features, BASELINE_FEATURES)

    baseline_if = (100, 0.05, "auto")
    baseline_hdbscan = (5, 3)
    rows = [score_configuration(baseline_features, labels, baseline_if, baseline_hdbscan, "baseline")]
    anomaly_masks = {}
    for if_config in IF_CONFIGS:
        n_estimators, contamination, max_samples = if_config
        fit_max_samples = int(np.sqrt(len(selected_features))) if max_samples == "sqrt" else max_samples
        model = IsolationForest(
            n_estimators=n_estimators, contamination=contamination,
            max_samples=fit_max_samples, random_state=42, n_jobs=-1,
        )
        anomaly_scores = model.fit(selected_features).decision_function(selected_features)
        anomaly_masks[if_config] = anomaly_scores <= np.quantile(anomaly_scores, 0.20)

    cluster_labels_by_config = {}
    for hdbscan_config in HDBSCAN_CONFIGS:
        min_cluster_size, min_samples = hdbscan_config
        cluster_labels_by_config[hdbscan_config] = TransactionClusteredModel(
            min_cluster_size=min_cluster_size, min_samples=min_samples,
        ).fit_predict(selected_features)

    for if_config, hdbscan_config in product(IF_CONFIGS, HDBSCAN_CONFIGS):
        rows.append(combine_predictions(
            labels, if_config, anomaly_masks[if_config], hdbscan_config,
            cluster_labels_by_config[hdbscan_config], "engineered",
        ))

    results = pd.DataFrame(rows)
    results = results.sort_values(["f1", "precision", "recall"], ascending=False).reset_index(drop=True)
    results.to_csv(os.path.join(output_dir, "unsupervised_tuning_results.csv"), index=False)
    best = results[results["feature_set"] == "engineered"].iloc[0].to_dict()
    baseline = results[results["feature_set"] == "baseline"].iloc[0].to_dict()
    summary = {
        "validation_wallets": int(len(labels)),
        "suspicious_wallets": int(labels.sum()),
        "normal_wallets": int((~labels).sum()),
        "features_added": [column for column in selected_columns if column not in BASELINE_FEATURES],
        "features_used_after_filtering": selected_columns,
        "dropped_baseline_redundant_features": [column for column in baseline_columns if column not in selected_columns],
        "baseline": baseline,
        "best": best,
        "genuine_improvement": bool(best["f1"] > baseline["f1"]),
    }
    with open(os.path.join(output_dir, "best_unsupervised_parameters.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print(f"Validation wallets: {len(labels)} ({int(labels.sum())} suspicious, {int((~labels).sum())} normal)")
    print(f"Features after finite/constant/redundancy filtering: {selected_columns}")
    print("\nBASELINE")
    print(pd.Series(baseline).to_string())
    print("\nBEST ENGINEERED CONFIGURATION")
    print(pd.Series(best).to_string())
    print(f"\nAll {len(results) - 1} engineered configurations saved to outputs/evaluation/unsupervised_tuning_results.csv")
    print("Full result columns include precision, recall, f1, tn, fp, fn, tp, detected_anomalies, number_of_clusters, and noise_entities.")


if __name__ == "__main__":
    main()
