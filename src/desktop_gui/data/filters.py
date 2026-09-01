"""
GUI Filters
-----------
Pure filtering functions for alerts, transactions, and graph nodes.

These are presentation-layer filters only.  They do NOT calculate risk,
anomaly, or any analytical value.  They simply narrow lists based on
user-selected criteria.

DO NOT add ML or analytical computation here.
"""

from __future__ import annotations

from src.desktop_gui.data.schemas import AlertRecord, TransactionRecord, GraphNode


def filter_alerts(
    alerts: list[AlertRecord],
    *,
    risk_level: str | None = None,
    entity_search: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
) -> list[AlertRecord]:
    """Return a filtered copy of the alerts list."""
    result = list(alerts)
    if risk_level and risk_level != "All":
        result = [a for a in result if a.risk_level == risk_level]
    if entity_search:
        q = entity_search.lower()
        result = [a for a in result if q in a.entity_id.lower()]
    if min_score is not None:
        result = [a for a in result if a.risk_score >= min_score]
    if max_score is not None:
        result = [a for a in result if a.risk_score <= max_score]
    return result


def filter_transactions(
    transactions: list[TransactionRecord],
    *,
    entity_id: str | None = None,
    flag: str | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
) -> list[TransactionRecord]:
    """Return a filtered copy of the transactions list."""
    result = list(transactions)
    if entity_id:
        q = entity_id.lower()
        result = [t for t in result if q in t.source.lower() or q in t.destination.lower()]
    if flag and flag != "All Flags":
        result = [t for t in result if t.flag == flag]
    if min_amount is not None:
        result = [t for t in result if t.amount_btc >= min_amount]
    if max_amount is not None:
        result = [t for t in result if t.amount_btc <= max_amount]
    return result


def filter_graph_nodes(
    nodes: list[GraphNode],
    *,
    types: set[str] | None = None,
    entity_id: str | None = None,
) -> list[GraphNode]:
    """Return a filtered copy of graph nodes."""
    result = list(nodes)
    if types is not None:
        result = [n for n in result if n.type in types]
    if entity_id:
        q = entity_id.lower()
        result = [n for n in result if q in n.id.lower() or q in n.label.lower()]
    return result
