"""
BATMAN Backend — Integration Stub
==================================

THIS MODULE IS AN INTERFACE STUB ONLY.

It defines the functions that Ankita's backend modules will implement.
Currently every function returns dev_data placeholders so the GUI can
run without the backend.

DO NOT implement ML, Isolation Forest, HDBSCAN, DBSCAN, feature
engineering, or analytical risk scoring in this file.
"""


def get_overview_stats() -> dict:
    """Return aggregate dashboard statistics."""
    from backend.data_manager import get_overview_stats as _get
    return _get()


def get_alerts() -> list[dict]:
    """Return ranked alert records."""
    from backend.data_manager import get_alerts as _get
    return _get()


def get_entity_details(entity_id: str) -> dict | None:
    """Return full profile for a single entity."""
    from backend.data_manager import get_entities
    return get_entities().get(entity_id)


def get_entity_ids() -> list[str]:
    """Return all known entity IDs."""
    from backend.data_manager import get_entity_ids as _get
    return _get()


def get_transactions() -> list[dict]:
    """Return transaction records."""
    from backend.data_manager import get_transactions as _get
    return _get()


def get_transaction_detail(tx_id: str) -> dict | None:
    """Return extended detail for a single transaction."""
    from backend.data_manager import get_tx_detail
    return get_tx_detail(tx_id)


def get_graph_data() -> dict:
    """Return graph nodes and edges."""
    from backend.data_manager import get_graph_data as _get
    nodes, edges, stats, cent = _get()
    return {"nodes": nodes, "edges": edges}


def get_graph_stats() -> dict:
    """Return graph statistics."""
    from backend.data_manager import get_graph_data as _get
    _, _, stats, _ = _get()
    return stats


def get_centrality() -> list[dict]:
    """Return centrality ranking."""
    from backend.data_manager import get_graph_data as _get
    _, _, _, cent = _get()
    return cent.to_dict('records')


def get_explainability(entity_id: str) -> dict | None:
    """Return explanation data for a single entity."""
    from backend.data_manager import get_entities
    ent = get_entities().get(entity_id)
    if ent:
        return {
            "anomaly_score": ent.get("anomaly_score", 0),
            "risk_score": ent.get("risk_score", 0),
            "top_features": ent.get("top_features", []),
            "evidence": ent.get("evidence", []),
            "human_reason": ent.get("explanation", "")
        }
    return None


def get_explainability_ids() -> list[str]:
    """Return entity IDs that have explainability data."""
    from backend.data_manager import get_entity_ids as _get
    return _get()

def get_scoreboard() -> dict:
    """Return top 10 anomalous entities activity over time."""
    from backend.data_manager import get_scoreboard as _get
    return _get()
