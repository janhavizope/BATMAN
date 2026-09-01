"""
Development / Placeholder Data
-------------------------------
Centralised mock datasets used by every frontend page during UI
development.  ALL values here are artificial and clearly marked.

When Ankita's backend is ready, each page will import from
``backend.*`` instead of this module.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Overview KPIs
# ---------------------------------------------------------------------------
DEV_OVERVIEW_STATS = {
    "total_transactions": 10_247,
    "total_wallets": 1_034,
    "total_ips": 512,
    "anomalous_entities": 187,
    "high_risk_entities": 43,
    "critical_alerts": 12,
}

# ---------------------------------------------------------------------------
# Alerts table
# ---------------------------------------------------------------------------
DEV_ALERTS_DF = pd.DataFrame(
    [
        {"Rank": 1,  "Entity ID": "W001", "Risk Score": 94, "Risk Level": "Critical", "Main Reason": "Rapid transfer chain across 8 wallets in 12 minutes"},
        {"Rank": 2,  "Entity ID": "W017", "Risk Score": 91, "Risk Level": "Critical", "Main Reason": "Fan-out to 23 unique wallets within 1 hour"},
        {"Rank": 3,  "Entity ID": "IP-192.168.4.22", "Risk Score": 88, "Risk Level": "Critical", "Main Reason": "Associated with 3 flagged wallets"},
        {"Rank": 4,  "Entity ID": "W045", "Risk Score": 85, "Risk Level": "High", "Main Reason": "Peeling chain: 12 sequential small-value splits"},
        {"Rank": 5,  "Entity ID": "W003", "Risk Score": 82, "Risk Level": "High", "Main Reason": "Unusually high transaction velocity (47 txns/hr)"},
        {"Rank": 6,  "Entity ID": "IP-10.0.0.88", "Risk Score": 79, "Risk Level": "High", "Main Reason": "Shared IP with wallets from 3 different ASNs"},
        {"Rank": 7,  "Entity ID": "W072", "Risk Score": 76, "Risk Level": "High", "Main Reason": "Large single transfer to dormant wallet"},
        {"Rank": 8,  "Entity ID": "W012", "Risk Score": 71, "Risk Level": "Medium", "Main Reason": "Circular transaction pattern detected"},
        {"Rank": 9,  "Entity ID": "W099", "Risk Score": 64, "Risk Level": "Medium", "Main Reason": "Transactions only during off-peak hours (2-5 AM)"},
        {"Rank": 10, "Entity ID": "IP-172.16.0.5", "Risk Score": 58, "Risk Level": "Medium", "Main Reason": "Possible VPN/proxy — low transaction correlation"},
        {"Rank": 11, "Entity ID": "W110", "Risk Score": 45, "Risk Level": "Low", "Main Reason": "Minor deviation from cluster centroid"},
        {"Rank": 12, "Entity ID": "W203", "Risk Score": 32, "Risk Level": "Low", "Main Reason": "Slightly elevated transaction count"},
    ]
)

# ---------------------------------------------------------------------------
# Entity Investigation profiles
# ---------------------------------------------------------------------------
DEV_ENTITIES = {
    "W001": {
        "entity_id": "W001",
        "risk_score": 94,
        "risk_level": "Critical",
        "anomaly_score": 0.91,
        "transaction_count": 87,
        "counterparty_count": 34,
        "timeline": [
            {"timestamp": "2026-01-15 08:00:00", "event": "First transaction observed"},
            {"timestamp": "2026-01-15 08:12:00", "event": "Rapid transfer chain started"},
            {"timestamp": "2026-01-15 08:22:00", "event": "Fan-out to 8 wallets"},
            {"timestamp": "2026-01-15 09:05:00", "event": "Peak velocity reached"},
            {"timestamp": "2026-01-15 09:45:00", "event": "Final peeling split"},
        ],
        "network_associations": [
            {"type": "IP", "value": "192.168.4.22"},
            {"type": "IP", "value": "10.0.0.15"},
            {"type": "ASN", "value": "AS13335 (Cloudflare)"},
            {"type": "Country", "value": "Unknown / Proxy"},
        ],
        "evidence": [
            "8 rapid sequential transfers within 12 minutes",
            "All destination wallets created within 24 hours",
            "Total value moved: 14.7 BTC",
            "No inbound transactions (source-only pattern)",
        ],
        "top_features": [
            {"feature": "tx_velocity_1h", "contribution": 0.32},
            {"feature": "fan_out_degree", "contribution": 0.25},
            {"feature": "wallet_age_days", "contribution": 0.18},
            {"feature": "unique_counterparties", "contribution": 0.14},
            {"feature": "temporal_regularity", "contribution": 0.11},
        ],
        "explanation": (
            "Wallet W001 is flagged as Critical primarily due to an extremely "
            "rapid transfer chain involving 8 destination wallets within a "
            "12-minute window. All destination wallets are newly created "
            "(<24 hours old) and the source wallet has no inbound history, "
            "strongly suggesting a money-laundering fan-out pattern."
        ),
    },
    "W017": {
        "entity_id": "W017",
        "risk_score": 91,
        "risk_level": "Critical",
        "anomaly_score": 0.88,
        "transaction_count": 156,
        "counterparty_count": 52,
        "timeline": [
            {"timestamp": "2026-01-14 22:00:00", "event": "Large inbound transfer (5.2 BTC)"},
            {"timestamp": "2026-01-14 22:15:00", "event": "Fan-out begins"},
            {"timestamp": "2026-01-14 23:10:00", "event": "23 unique wallets received funds"},
        ],
        "network_associations": [
            {"type": "IP", "value": "10.0.0.33"},
            {"type": "ASN", "value": "AS16509 (Amazon AWS)"},
            {"type": "Country", "value": "Germany"},
        ],
        "evidence": [
            "Fan-out to 23 wallets in under 1 hour",
            "Consistent sub-0.01 BTC amounts to each destination",
            "Destination wallets share 2 common IP addresses",
        ],
        "top_features": [
            {"feature": "fan_out_degree", "contribution": 0.38},
            {"feature": "value_uniformity", "contribution": 0.27},
            {"feature": "counterparty_ip_overlap", "contribution": 0.20},
            {"feature": "temporal_regularity", "contribution": 0.15},
        ],
        "explanation": (
            "Wallet W017 shows a textbook fan-out pattern: a single large "
            "deposit is immediately split into 23 near-identical amounts "
            "sent to newly observed wallets. Several destination wallets "
            "share IP addresses, indicating coordinated control."
        ),
    },
    "W045": {
        "entity_id": "W045",
        "risk_score": 85,
        "risk_level": "High",
        "anomaly_score": 0.83,
        "transaction_count": 42,
        "counterparty_count": 14,
        "timeline": [
            {"timestamp": "2026-01-15 03:00:00", "event": "Peeling chain initiated"},
            {"timestamp": "2026-01-15 03:45:00", "event": "12 sequential splits completed"},
        ],
        "network_associations": [
            {"type": "IP", "value": "172.16.0.9"},
            {"type": "ASN", "value": "AS24940 (Hetzner)"},
            {"type": "Country", "value": "Finland"},
        ],
        "evidence": [
            "12 sequential peeling splits with decreasing amounts",
            "Each split leaves a small residue in the peeling wallet",
            "Final sweep consolidates into a single destination",
        ],
        "top_features": [
            {"feature": "peeling_chain_length", "contribution": 0.40},
            {"feature": "value_decrease_pattern", "contribution": 0.30},
            {"feature": "tx_interval_regularity", "contribution": 0.20},
        ],
        "explanation": (
            "Wallet W045 executed a classic 12-step peeling chain where "
            "each transaction peels off a small amount to a new address "
            "before forwarding the remainder. This obfuscates the "
            "transaction trail and is a common laundering technique."
        ),
    },
}

# ---------------------------------------------------------------------------
# Entity list (for selectbox)
# ---------------------------------------------------------------------------
DEV_ENTITY_IDS = list(DEV_ENTITIES.keys())

# ---------------------------------------------------------------------------
# Transaction details
# ---------------------------------------------------------------------------
DEV_TRANSACTIONS = pd.DataFrame(
    [
        {"Transaction ID": "TX-001", "Amount (BTC)": 1.2500, "Timestamp": "2026-01-15 08:00:00", "Source": "W001", "Destination": "W017", "Flag": "Suspicious"},
        {"Transaction ID": "TX-002", "Amount (BTC)": 0.0500, "Timestamp": "2026-01-15 08:03:00", "Source": "W001", "Destination": "W045", "Flag": "Normal"},
        {"Transaction ID": "TX-003", "Amount (BTC)": 0.0500, "Timestamp": "2026-01-15 08:06:00", "Source": "W001", "Destination": "W072", "Flag": "Normal"},
        {"Transaction ID": "TX-004", "Amount (BTC)": 0.0500, "Timestamp": "2026-01-15 08:09:00", "Source": "W001", "Destination": "W012", "Flag": "Normal"},
        {"Transaction ID": "TX-005", "Amount (BTC)": 0.0500, "Timestamp": "2026-01-15 08:12:00", "Source": "W001", "Destination": "W099", "Flag": "Normal"},
        {"Transaction ID": "TX-006", "Amount (BTC)": 0.2200, "Timestamp": "2026-01-15 08:15:00", "Source": "W001", "Destination": "W110", "Flag": "Normal"},
        {"Transaction ID": "TX-007", "Amount (BTC)": 5.2000, "Timestamp": "2026-01-15 09:00:00", "Source": "W017", "Destination": "W203", "Flag": "Suspicious"},
        {"Transaction ID": "TX-008", "Amount (BTC)": 0.1500, "Timestamp": "2026-01-15 09:05:00", "Source": "W017", "Destination": "W045", "Flag": "Normal"},
        {"Transaction ID": "TX-009", "Amount (BTC)": 0.3300, "Timestamp": "2026-01-15 09:30:00", "Source": "W045", "Destination": "W003", "Flag": "Normal"},
        {"Transaction ID": "TX-010", "Amount (BTC)": 0.0100, "Timestamp": "2026-01-15 10:00:00", "Source": "W003", "Destination": "W072", "Flag": "Suspicious"},
    ]
)

# Single transaction detail (for detail view)
DEV_TX_DETAIL = {
    "transaction_id": "TX-001",
    "amount_btc": 1.2500,
    "timestamp": "2026-01-15 08:00:00",
    "source": "W001",
    "destination": "W017",
    "confirmations": 847,
    "fee_btc": 0.00012,
    "block_height": 828_412,
    "flag": "Suspicious",
    "reason": "Part of rapid transfer chain — first hop",
}

# ---------------------------------------------------------------------------
# Network graph (small dev example)
# ---------------------------------------------------------------------------
DEV_GRAPH_NODES = [
    {"id": "W001",  "type": "Wallet",     "label": "W001",  "risk_score": 94},
    {"id": "W017",  "type": "Wallet",     "label": "W017",  "risk_score": 91},
    {"id": "W045",  "type": "Wallet",     "label": "W045",  "risk_score": 85},
    {"id": "W072",  "type": "Wallet",     "label": "W072",  "risk_score": 76},
    {"id": "W012",  "type": "Wallet",     "label": "W012",  "risk_score": 71},
    {"id": "TX001", "type": "Transaction","label": "TX-001","risk_score": 0},
    {"id": "TX007", "type": "Transaction","label": "TX-007","risk_score": 0},
    {"id": "IP1",   "type": "IP",         "label": "192.168.4.22", "risk_score": 88},
    {"id": "IP2",   "type": "IP",         "label": "10.0.0.33",    "risk_score": 79},
    {"id": "ASN1",  "type": "ASN",        "label": "AS13335",      "risk_score": 0},
    {"id": "C1",    "type": "Country",    "label": "Germany",      "risk_score": 0},
]

DEV_GRAPH_EDGES = [
    {"source": "W001",  "target": "TX001", "relation": "sent"},
    {"source": "TX001", "target": "W017",  "relation": "received"},
    {"source": "W017",  "target": "TX007", "relation": "sent"},
    {"source": "TX007", "target": "W045",  "relation": "received"},
    {"source": "W001",  "target": "W072",  "relation": "sent_direct"},
    {"source": "W001",  "target": "W012",  "relation": "sent_direct"},
    {"source": "IP1",   "target": "W001",  "relation": "associated"},
    {"source": "IP2",   "target": "W017",  "relation": "associated"},
    {"source": "IP1",   "target": "ASN1",  "relation": "belongs_to"},
    {"source": "IP2",   "target": "ASN1",  "relation": "belongs_to"},
    {"source": "ASN1",  "target": "C1",    "relation": "located_in"},
]

DEV_GRAPH_STATS = {
    "total_nodes": len(DEV_GRAPH_NODES),
    "total_edges": len(DEV_GRAPH_EDGES),
    "clusters_detected": 2,
    "avg_degree": round(2 * len(DEV_GRAPH_EDGES) / len(DEV_GRAPH_NODES), 2),
}

DEV_CENTRALITY_TABLE = pd.DataFrame(
    [
        {"Rank": 1, "Node": "W001", "Centrality Score": 0.82, "Cluster": 0},
        {"Rank": 2, "Node": "W017", "Centrality Score": 0.67, "Cluster": 0},
        {"Rank": 3, "Node": "TX001","Centrality Score": 0.54, "Cluster": 0},
    ]
)

# ---------------------------------------------------------------------------
# Explainability
# ---------------------------------------------------------------------------
DEV_EXPLAINABILITY = {
    "W001": {
        "anomaly_score": 0.91,
        "risk_score": 94,
        "top_features": [
            {"feature": "tx_velocity_1h",         "contribution": 0.32, "direction": "increases"},
            {"feature": "fan_out_degree",          "contribution": 0.25, "direction": "increases"},
            {"feature": "wallet_age_days",         "contribution": 0.18, "direction": "increases"},
            {"feature": "unique_counterparties",   "contribution": 0.14, "direction": "increases"},
            {"feature": "temporal_regularity",     "contribution": 0.11, "direction": "increases"},
        ],
        "evidence": [
            "8 rapid sequential transfers within 12 minutes",
            "All 8 destination wallets created within 24 hours",
            "Zero inbound transactions — source-only pattern",
            "Transaction velocity (47 txns/hr) is 12x the cluster average",
        ],
        "human_reason": (
            "This wallet is flagged Critical because it initiated an extremely "
            "rapid fan-out of funds to 8 newly created wallets within 12 minutes. "
            "The wallet has no inbound transaction history and the transaction "
            "velocity is 12 times higher than the cluster average, strongly "
            "suggesting automated laundering activity."
        ),
    },
    "W017": {
        "anomaly_score": 0.88,
        "risk_score": 91,
        "top_features": [
            {"feature": "fan_out_degree",          "contribution": 0.38, "direction": "increases"},
            {"feature": "value_uniformity",        "contribution": 0.27, "direction": "increases"},
            {"feature": "counterparty_ip_overlap",  "contribution": 0.20, "direction": "increases"},
            {"feature": "temporal_regularity",     "contribution": 0.15, "direction": "increases"},
        ],
        "evidence": [
            "Fan-out to 23 wallets with near-identical amounts",
            "6 destination wallets share 2 IP addresses",
            "Single large inbound transfer preceded the fan-out",
        ],
        "human_reason": (
            "Wallet W017 received a large deposit and immediately distributed "
            "it in uniform amounts to 23 wallets. Multiple destination wallets "
            "share IP addresses, indicating coordinated control by a single entity."
        ),
    },
    "W045": {
        "anomaly_score": 0.83,
        "risk_score": 85,
        "top_features": [
            {"feature": "peeling_chain_length",    "contribution": 0.40, "direction": "increases"},
            {"feature": "value_decrease_pattern",  "contribution": 0.30, "direction": "increases"},
            {"feature": "tx_interval_regularity",  "contribution": 0.20, "direction": "increases"},
        ],
        "evidence": [
            "12 sequential peeling splits with monotonically decreasing amounts",
            "Consistent 5-minute interval between splits",
            "Final sweep consolidates remainder into one address",
        ],
        "human_reason": (
            "Wallet W045 executed a classic peeling chain of 12 steps, where each "
            "transaction peels off a small amount before forwarding the remainder. "
            "The regular timing and decreasing amounts are hallmarks of automated "
            "peeling scripts."
        ),
    },
}

DEV_EXPLAINABILITY_IDS = list(DEV_EXPLAINABILITY.keys())
