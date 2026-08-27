"""
GUI Data Layer
--------------
Contracts, data loading, and filtering for the BATMAN GUI.
"""

from gui.data.schemas import (
    OverviewStats,
    AlertRecord,
    EntityProfile,
    TransactionRecord,
    GraphData,
    GraphNode,
    GraphEdge,
    ExplanationRecord,
)
from gui.data.data_manager import DataManager
from gui.data.filters import (
    filter_alerts,
    filter_transactions,
    filter_graph_nodes,
)

__all__ = [
    "OverviewStats", "AlertRecord", "EntityProfile", "TransactionRecord",
    "GraphData", "GraphNode", "GraphEdge", "ExplanationRecord",
    "DataManager",
    "filter_alerts", "filter_transactions", "filter_graph_nodes",
]
