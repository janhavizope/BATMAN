"""
train_model.py
----------------
Trains a Random Forest classifier to detect illicit Bitcoin transactions
using the synthetic dataset produced by generate_synthetic_data.py.

Steps:
    1. Load CSV
    2. Feature engineering (drop IDs/addresses, derive numeric features,
       encode IP into a coarse feature instead of raw string)
    3. Train/test split (stratified, since classes are imbalanced)
    4. Train RandomForestClassifier
    5. Evaluate: accuracy, precision/recall/F1, confusion matrix, ROC-AUC
    6. Save the trained model + feature list with joblib

Run:
    python3 train_model.py
"""

import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    RocCurveDisplay,
)

DATA_FILE = "synthetic_bitcoin_transactions.csv"
MODEL_FILE = "illicit_tx_rf_model.joblib"


def load_and_engineer_features(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])

    # --- derived numeric features ---
    df["fee_to_amount_ratio"] = df["fee_btc"] / df["amount_btc"].replace(0, np.nan)
    df["fee_to_amount_ratio"] = df["fee_to_amount_ratio"].fillna(0)

    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    df["fan_ratio"] = df["num_outputs"] / df["num_inputs"].replace(0, np.nan)
    df["fan_ratio"] = df["fan_ratio"].fillna(0)

    # coarse IP feature: first octet as a category-ish numeric bucket
    df["ip_first_octet"] = df["ip_address"].str.split(".").str[0].astype(int)

    feature_cols = [
        "amount_btc",
        "fee_btc",
        "fee_to_amount_ratio",
        "num_inputs",
        "num_outputs",
        "fan_ratio",
        "is_new_address_out",
        "tx_per_hour_sender",
        "hour_of_day",
        "day_of_week",
        "ip_first_octet",
    ]

    X = df[feature_cols]
    y = df["is_illicit"]
    return X, y, feature_cols


def main():
    print(f"Loading {DATA_FILE} ...")
    X, y, feature_cols = load_and_engineer_features(DATA_FILE)
    print(f"Loaded {len(X)} rows, {len(feature_cols)} features")
    print(f"Class balance:\n{y.value_counts(normalize=True)}\n")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        class_weight="balanced",   # important given ~12% positive class
        random_state=42,
        n_jobs=-1,
    )

    print("Training RandomForestClassifier ...")
    model.fit(X_train, y_train)

    # --- evaluation ---
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=["legit", "illicit"]))

    print("=== Confusion Matrix ===")
    cm = confusion_matrix(y_test, y_pred)
    print(pd.DataFrame(
        cm,
        index=["actual_legit", "actual_illicit"],
        columns=["pred_legit", "pred_illicit"],
    ))

    auc = roc_auc_score(y_test, y_proba)
    print(f"\nROC-AUC: {auc:.4f}")

    print("\n=== Feature Importances ===")
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    print(importances.sort_values(ascending=False).round(4))

    # --- save model ---
    joblib.dump({"model": model, "feature_cols": feature_cols}, MODEL_FILE)
    print(f"\nSaved trained model to {MODEL_FILE}")


if __name__ == "__main__":
    main()
