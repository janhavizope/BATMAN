"""
risk_engine.py
Combines behavioral, anomaly, graph, temporal, transaction, network, and
cluster signals into a 0-100 wallet risk score.
"""

import json
import os
import sys
from typing import Dict, List
from pathlib import Path

import numpy as np
import pandas as pd

# Allow the script to be run directly from the repository root.
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(REPO_ROOT))


# Signed point-biserial correlations from the wallet-level validation run.
# Magnitudes determine relative importance; negative values are inverted when
# the behavioral component is calculated because lower values indicate risk.
WEIGHTS = {
    "avg_fee": -0.625129,
    "avg_inter_arrival_time": -0.617916,
    "avg_output_count": -0.591322,
    "unique_country_count": -0.463269,
    "avg_input_count": -0.435490,
    "unique_counterparties": -0.431899,
    "min_pass_through_gap": -0.429034,
    "unique_ip_count": -0.408988,
    "unique_asn_count": -0.394286,
    "out_degree": -0.388439,
    "total_sent": -0.386329,
    "degree": -0.382843,
    "degree_centrality": -0.382843,
    "total_tx_count": -0.353493,
    "betweenness_centrality": -0.332774,
    "total_received": -0.318196,
    "in_degree": -0.310542,
    "avg_amount": -0.264754,
    "tx_per_hour": 0.229708,
    "burst_count": 0.140767,
    "max_tx_in_window": 0.109596,
}


def min_max_scale(values: pd.Series, invert: bool = False) -> pd.Series:
    """Scale a numeric series to 0-100, optionally reversing its direction."""
    minimum = values.min()
    maximum = values.max()
    value_range = maximum - minimum

    if value_range == 0:
        scaled = pd.Series(0.0, index=values.index)
    else:
        scaled = (values - minimum) / value_range * 100

    return 100 - scaled if invert else scaled


from src.core.backend.ingestion.ingestor import TransactionIngestor

def load_ground_truth(csv_path: str) -> pd.DataFrame:
    """Return one suspicious/not-suspicious ground-truth row per wallet."""
    ingestor = TransactionIngestor()
    raw_df, _ = ingestor.ingest(csv_path)
    wallet_truth: Dict[str, bool] = {}

    for _, row in raw_df.iterrows():
        input_wallets = row.get("input_addresses[]", [])
        output_wallets = row.get("output_addresses[]", [])

        if not isinstance(input_wallets, list):
            input_wallets = []
        if not isinstance(output_wallets, list):
            output_wallets = []

        is_suspicious = bool(row.get("is_suspicious", False))
        if isinstance(row.get("is_suspicious"), str):
            is_suspicious = row["is_suspicious"].strip().lower() == "true"

        for wallet in input_wallets + output_wallets:
            wallet_truth[wallet] = wallet_truth.get(wallet, False) or is_suspicious

    return pd.DataFrame(
        {"actual_suspicious": wallet_truth.values()},
        index=pd.Index(wallet_truth.keys(), name="wallet_address"),
    )


def add_normalized_components(df: pd.DataFrame) -> pd.DataFrame:
    """Add 0-100 risk components for each scoring category."""
    result = df.copy()

    # Isolation Forest assigns lower scores to more anomalous observations.
    result["anomaly_component"] = min_max_scale(result["anomaly_score"], invert=True)
    result["graph_component"] = (
        min_max_scale(result["degree"])
        + min_max_scale(result["betweenness_centrality"])
    ) / 2
    result["temporal_component"] = (
        min_max_scale(result["avg_inter_arrival_time"])
        + min_max_scale(result["burst_count"])
    ) / 2
    result["transaction_component"] = (
        min_max_scale(result["avg_amount"])
        + min_max_scale(result["total_tx_count"])
    ) / 2
    result["network_component"] = (
        min_max_scale(result["unique_ip_count"])
        + min_max_scale(result["unique_asn_count"])
    ) / 2
    result["cluster_component"] = (result["cluster_id"] == -1).astype(float) * 100

    weighted_features = pd.Series(0.0, index=result.index)
    available_weight = 0.0
    for feature, correlation in WEIGHTS.items():
        if feature not in result.columns:
            continue
        weight = abs(correlation)
        weighted_features += min_max_scale(result[feature], invert=correlation < 0) * weight
        available_weight += weight

    if available_weight:
        result["behavioral_component"] = weighted_features / available_weight
    else:
        result["behavioral_component"] = 0.0

    result["risk_score"] = (
        result["behavioral_component"] * 0.60
        + result["anomaly_component"] * 0.20
        + result["cluster_component"] * 0.20
    ).clip(0, 100)
    return result


def risk_level(score: float) -> str:
    """Map a numeric risk score to the requested label range."""
    if score <= 30:
        return "LOW"
    if score <= 60:
        return "MEDIUM"
    if score <= 80:
        return "HIGH"
    return "CRITICAL"


def build_reasons(row: pd.Series, averages: pd.Series) -> List[str]:
    """Return the two or three strongest plain-text deviations for a wallet."""
    candidates = []

    # Positive deviations use high-is-risky behavior; anomaly scores are reversed.
    for column, reason, direction in [
        ("anomaly_score", "unusually anomalous behavior", "lower"),
        ("degree", "unusually high transaction connectivity", "higher"),
        ("betweenness_centrality", "unusually high intermediary connectivity", "higher"),
        ("avg_inter_arrival_time", "unusually long transaction intervals", "higher"),
        ("burst_count", "unusually frequent transaction bursts", "higher"),
        ("avg_amount", "unusually high transaction amounts", "higher"),
        ("total_tx_count", "unusually high transaction volume", "higher"),
        ("unique_ip_count", "unusually high network diversity", "higher"),
        ("unique_asn_count", "unusually high provider diversity", "higher"),
    ]:
        average = averages[column]
        difference = average - row[column] if direction == "lower" else row[column] - average
        spread = max(abs(averages[column]), 1e-12)
        relative_difference = difference / spread
        if relative_difference > 0:
            candidates.append((relative_difference, reason))

    if row["cluster_id"] == -1:
        candidates.append((1.0, "isolated as an HDBSCAN cluster outlier"))

    candidates.sort(reverse=True)
    reasons = [reason for _, reason in candidates[:3]]
    fallback_reasons = [
        "behavior is close to the dataset average",
        "no other dominant risk signal",
    ]
    while len(reasons) < 2:
        reasons.append(fallback_reasons[len(reasons)])
    return reasons


def main() -> None:
    """Build and save the final wallet risk results."""
    REPO_ROOT = Path(__file__).resolve().parents[4]
    features_path = str(REPO_ROOT / "data" / "dev" / "features.parquet")
    anomaly_path = str(REPO_ROOT / "data" / "dev" / "anomaly_scores.parquet")
    cluster_path = str(REPO_ROOT / "data" / "dev" / "cluster_labels.parquet")
    raw_path = str(REPO_ROOT / "data" / "dev" / "dev_dataset_50k.csv")
    output_path = str(REPO_ROOT / "data" / "dev" / "results.json")

    required_paths = [features_path, anomaly_path, cluster_path, raw_path]
    missing_paths = [path for path in required_paths if not os.path.exists(path)]
    if missing_paths:
        print(f"Error: required input not found: {missing_paths}")
        sys.exit(1)

    print("Loading feature, anomaly, cluster, and ground-truth data...")
    features_df = pd.read_parquet(features_path)
    anomaly_df = pd.read_parquet(anomaly_path)[["anomaly_score"]]
    cluster_df = pd.read_parquet(cluster_path)[["cluster_id"]]

    # All model outputs use wallet_address as their index, so no entity mapping
    # is needed and every join remains aligned to the unique wallet key.
    result_df = features_df.join(anomaly_df, how="inner").join(cluster_df, how="inner")
    if result_df.empty:
        print("Error: no wallets were shared across the three parquet files.")
        sys.exit(1)

    result_df = add_normalized_components(result_df)
    averages = result_df[
        [
            "anomaly_score", "degree", "betweenness_centrality",
            "avg_inter_arrival_time", "burst_count", "avg_amount",
            "total_tx_count", "unique_ip_count", "unique_asn_count",
        ]
    ].mean()
    result_df["risk_level"] = result_df["risk_score"].map(risk_level)
    result_df["top_reasons"] = result_df.apply(
        lambda row: build_reasons(row, averages), axis=1
    )

    ground_truth_df = load_ground_truth(raw_path)
    result_df = result_df.join(ground_truth_df, how="left")
    result_df["actual_suspicious"] = (
        result_df["actual_suspicious"].astype("boolean").fillna(False).astype(bool)
    )

    output_columns = [
        "risk_score", "risk_level", "anomaly_score", "cluster_id", "top_reasons",
        "total_tx_count", "unique_counterparties",
    ]
    output_df = result_df[output_columns].reset_index()
    output_df["risk_score"] = output_df["risk_score"].round(2)
    output_df = output_df.sort_values("risk_score", ascending=False)
    output_df.to_json(output_path, orient="records", indent=2)

    print(f"Saved {len(output_df)} wallet results to {output_path}")
    print("\n--- TOP 10 RISKIEST WALLETS ---")
    print(output_df.head(10).to_string(index=False))

    flagged = result_df[ result_df["risk_level"].isin(["HIGH", "CRITICAL"]) ]
    true_positives = int(flagged["actual_suspicious"].sum())
    actual_suspicious = int(result_df["actual_suspicious"].sum())
    precision = true_positives / len(flagged) if len(flagged) else 0.0
    recall = true_positives / actual_suspicious if actual_suspicious else 0.0
    print("\n--- VALIDATION ---")
    print(f"High/Critical flagged wallets marked suspicious: {true_positives}/{len(flagged)}")
    print(f"Precision: {precision:.2%}")
    print(f"Suspicious wallets caught: {true_positives}/{actual_suspicious}")
    print(f"Recall: {recall:.2%}")


if __name__ == "__main__":
    main()
