"""
Development / Placeholder Data
-------------------------------
Centralised mock datasets used by every GUI page during UI development.
ALL values here are artificial and clearly marked.

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
DEV_ALERTS = [
    {"Rank": 1,  "Entity ID": "W001",             "Risk Score": 94, "Risk Level": "Critical", "Main Reason": "Rapid transfer chain across 8 wallets in 12 minutes"},
    {"Rank": 2,  "Entity ID": "W017",             "Risk Score": 91, "Risk Level": "Critical", "Main Reason": "Fan-out to 23 unique wallets within 1 hour"},
    {"Rank": 3,  "Entity ID": "IP-192.168.4.22",  "Risk Score": 88, "Risk Level": "Critical", "Main Reason": "Associated with 3 flagged wallets"},
    {"Rank": 4,  "Entity ID": "W045",             "Risk Score": 85, "Risk Level": "High",     "Main Reason": "Peeling chain: 12 sequential small-value splits"},
    {"Rank": 5,  "Entity ID": "W003",             "Risk Score": 82, "Risk Level": "High",     "Main Reason": "Unusually high transaction velocity (47 txns/hr)"},
    {"Rank": 6,  "Entity ID": "IP-10.0.0.88",     "Risk Score": 79, "Risk Level": "High",     "Main Reason": "Shared IP with wallets from 3 different ASNs"},
    {"Rank": 7,  "Entity ID": "W072",             "Risk Score": 76, "Risk Level": "High",     "Main Reason": "Large single transfer to dormant wallet"},
    {"Rank": 8,  "Entity ID": "W012",             "Risk Score": 71, "Risk Level": "Medium",   "Main Reason": "Circular transaction pattern detected"},
    {"Rank": 9,  "Entity ID": "W099",             "Risk Score": 64, "Risk Level": "Medium",   "Main Reason": "Transactions only during off-peak hours (2-5 AM)"},
    {"Rank": 10, "Entity ID": "IP-172.16.0.5",    "Risk Score": 58, "Risk Level": "Medium",   "Main Reason": "Possible VPN/proxy — low transaction correlation"},
    {"Rank": 11, "Entity ID": "W110",             "Risk Score": 45, "Risk Level": "Low",      "Main Reason": "Minor deviation from cluster centroid"},
    {"Rank": 12, "Entity ID": "W203",             "Risk Score": 32, "Risk Level": "Low",      "Main Reason": "Slightly elevated transaction count"},
]

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

DEV_ENTITY_IDS = list(DEV_ENTITIES.keys())

# ---------------------------------------------------------------------------
# Transaction details
# ---------------------------------------------------------------------------
DEV_TRANSACTIONS = [
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
import random

# Generate a massive clustered graph (High-Level simulation)
DEV_GRAPH_NODES = []
DEV_GRAPH_EDGES = []

_hubs = [f"HUB_{i}" for i in range(10)]
for h in _hubs:
    DEV_GRAPH_NODES.append({"id": h, "type": "Wallet", "label": h, "risk_score": 95})

for i in range(250):
    nid = f"N_{i}"
    ntype = random.choices(["Wallet", "Transaction", "IP", "ASN"], weights=[50, 30, 15, 5])[0]
    DEV_GRAPH_NODES.append({"id": nid, "type": ntype, "label": "", "risk_score": random.randint(0, 100)})
    
    # Attach to a random hub to create clusters
    hub = random.choice(_hubs)
    DEV_GRAPH_EDGES.append({"source": hub, "target": nid, "relation": "linked"})
    
    # Randomly interconnect some peripheral nodes
    if random.random() > 0.85 and i > 0:
        DEV_GRAPH_EDGES.append({"source": nid, "target": f"N_{random.randint(0, i-1)}", "relation": "peer"})

DEV_GRAPH_STATS = {
    "total_nodes": len(DEV_GRAPH_NODES),
    "total_edges": len(DEV_GRAPH_EDGES),
    "clusters_detected": 2,
    "avg_degree": round(2 * len(DEV_GRAPH_EDGES) / len(DEV_GRAPH_NODES), 2),
}

DEV_CENTRALITY = [
    {"Rank": 1, "Node": "W001",  "Centrality Score": 0.82, "Cluster": 0},
    {"Rank": 2, "Node": "W017",  "Centrality Score": 0.67, "Cluster": 0},
    {"Rank": 3, "Node": "TX001", "Centrality Score": 0.54, "Cluster": 0},
]

# ---------------------------------------------------------------------------
# Explainability
# ---------------------------------------------------------------------------
DEV_EXPLAINABILITY = {
    "W001": {
        "anomaly_score": 0.91,
        "risk_score": 94,
        "top_features": [
            {"feature": "tx_velocity_1h",       "contribution": 0.32, "direction": "increases"},
            {"feature": "fan_out_degree",        "contribution": 0.25, "direction": "increases"},
            {"feature": "wallet_age_days",       "contribution": 0.18, "direction": "increases"},
            {"feature": "unique_counterparties", "contribution": 0.14, "direction": "increases"},
            {"feature": "temporal_regularity",   "contribution": 0.11, "direction": "increases"},
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
            {"feature": "fan_out_degree",         "contribution": 0.38, "direction": "increases"},
            {"feature": "value_uniformity",       "contribution": 0.27, "direction": "increases"},
            {"feature": "counterparty_ip_overlap", "contribution": 0.20, "direction": "increases"},
            {"feature": "temporal_regularity",    "contribution": 0.15, "direction": "increases"},
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
            {"feature": "peeling_chain_length",   "contribution": 0.40, "direction": "increases"},
            {"feature": "value_decrease_pattern", "contribution": 0.30, "direction": "increases"},
            {"feature": "tx_interval_regularity", "contribution": 0.20, "direction": "increases"},
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


# Scoreboard Data
DEV_SCOREBOARD_DATA = {
    "Wallet (W001)": [
        {
            "time": "14:30",
            "score": 57
        },
        {
            "time": "15:00",
            "score": 73
        },
        {
            "time": "15:30",
            "score": 287
        },
        {
            "time": "16:00",
            "score": 397
        },
        {
            "time": "16:30",
            "score": 632
        },
        {
            "time": "17:00",
            "score": 667
        },
        {
            "time": "17:30",
            "score": 853
        },
        {
            "time": "18:00",
            "score": 936
        },
        {
            "time": "18:30",
            "score": 1097
        }
    ],
    "Wallet (W017)": [
        {
            "time": "14:30",
            "score": 12
        },
        {
            "time": "15:00",
            "score": 27
        },
        {
            "time": "15:30",
            "score": 139
        },
        {
            "time": "16:00",
            "score": 311
        },
        {
            "time": "16:30",
            "score": 585
        },
        {
            "time": "17:00",
            "score": 608
        },
        {
            "time": "17:30",
            "score": 691
        },
        {
            "time": "18:00",
            "score": 927
        },
        {
            "time": "18:30",
            "score": 1132
        }
    ],
    "Wallet (W045)": [
        {
            "time": "14:30",
            "score": 140
        },
        {
            "time": "15:00",
            "score": 187
        },
        {
            "time": "15:30",
            "score": 416
        },
        {
            "time": "16:00",
            "score": 468
        },
        {
            "time": "16:30",
            "score": 531
        },
        {
            "time": "17:00",
            "score": 647
        },
        {
            "time": "17:30",
            "score": 836
        },
        {
            "time": "18:00",
            "score": 1030
        },
        {
            "time": "18:30",
            "score": 1167
        }
    ],
    "IP (192.168.4.22)": [
        {
            "time": "14:30",
            "score": 125
        },
        {
            "time": "15:00",
            "score": 236
        },
        {
            "time": "15:30",
            "score": 378
        },
        {
            "time": "16:00",
            "score": 425
        },
        {
            "time": "16:30",
            "score": 618
        },
        {
            "time": "17:00",
            "score": 766
        },
        {
            "time": "17:30",
            "score": 947
        },
        {
            "time": "18:00",
            "score": 1085
        },
        {
            "time": "18:30",
            "score": 1118
        }
    ],
    "Wallet (W072)": [
        {
            "time": "14:30",
            "score": 114
        },
        {
            "time": "15:00",
            "score": 233
        },
        {
            "time": "15:30",
            "score": 236
        },
        {
            "time": "16:00",
            "score": 430
        },
        {
            "time": "16:30",
            "score": 470
        },
        {
            "time": "17:00",
            "score": 510
        },
        {
            "time": "17:30",
            "score": 617
        },
        {
            "time": "18:00",
            "score": 902
        },
        {
            "time": "18:30",
            "score": 1010
        }
    ],
    "Wallet (W012)": [
        {
            "time": "14:30",
            "score": 71
        },
        {
            "time": "15:00",
            "score": 329
        },
        {
            "time": "15:30",
            "score": 410
        },
        {
            "time": "16:00",
            "score": 459
        },
        {
            "time": "16:30",
            "score": 741
        },
        {
            "time": "17:00",
            "score": 860
        },
        {
            "time": "17:30",
            "score": 996
        },
        {
            "time": "18:00",
            "score": 1108
        },
        {
            "time": "18:30",
            "score": 1398
        }
    ],
    "IP (10.0.0.33)": [
        {
            "time": "14:30",
            "score": 52
        },
        {
            "time": "15:00",
            "score": 65
        },
        {
            "time": "15:30",
            "score": 281
        },
        {
            "time": "16:00",
            "score": 464
        },
        {
            "time": "16:30",
            "score": 614
        },
        {
            "time": "17:00",
            "score": 665
        },
        {
            "time": "17:30",
            "score": 701
        },
        {
            "time": "18:00",
            "score": 867
        },
        {
            "time": "18:30",
            "score": 1028
        }
    ],
    "Wallet (W999)": [
        {
            "time": "14:30",
            "score": 279
        },
        {
            "time": "15:00",
            "score": 566
        },
        {
            "time": "15:30",
            "score": 740
        },
        {
            "time": "16:00",
            "score": 916
        },
        {
            "time": "16:30",
            "score": 1101
        },
        {
            "time": "17:00",
            "score": 1295
        },
        {
            "time": "17:30",
            "score": 1382
        },
        {
            "time": "18:00",
            "score": 1410
        },
        {
            "time": "18:30",
            "score": 1518
        }
    ],
    "ASN (AS13335)": [
        {
            "time": "14:30",
            "score": 44
        },
        {
            "time": "15:00",
            "score": 145
        },
        {
            "time": "15:30",
            "score": 287
        },
        {
            "time": "16:00",
            "score": 422
        },
        {
            "time": "16:30",
            "score": 717
        },
        {
            "time": "17:00",
            "score": 859
        },
        {
            "time": "17:30",
            "score": 1132
        },
        {
            "time": "18:00",
            "score": 1249
        },
        {
            "time": "18:30",
            "score": 1504
        }
    ],
    "Wallet (W888)": [
        {
            "time": "14:30",
            "score": 216
        },
        {
            "time": "15:00",
            "score": 495
        },
        {
            "time": "15:30",
            "score": 574
        },
        {
            "time": "16:00",
            "score": 596
        },
        {
            "time": "16:30",
            "score": 694
        },
        {
            "time": "17:00",
            "score": 926
        },
        {
            "time": "17:30",
            "score": 1051
        },
        {
            "time": "18:00",
            "score": 1067
        },
        {
            "time": "18:30",
            "score": 1269
        }
    ]
}
