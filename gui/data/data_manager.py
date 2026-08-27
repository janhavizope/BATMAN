"""
GUI Data Manager
----------------
Central facade for loading data into the GUI.

Supports two modes:
1. DEV mode  — loads from gui.dev_data (placeholder).
2. LIVE mode — loads from backend.* modules (future).

The DataManager does NOT perform analytical computation.
It only loads and converts data into schema objects.

DO NOT implement ML, risk scoring, or correlation here.
"""

from __future__ import annotations

from gui.data.schemas import (
    OverviewStats, AlertRecord, EntityProfile,
    TransactionRecord, GraphData, ExplanationRecord,
)


class DataManager:
    """Single point of truth for GUI data access."""

    def __init__(self):
        self._overview: OverviewStats | None = None
        self._alerts: list[AlertRecord] = []
        self._entities: dict[str, EntityProfile] = {}
        self._transactions: list[TransactionRecord] = []
        self._graph: GraphData | None = None
        self._explanations: dict[str, ExplanationRecord] = {}
        self._loaded = False

    @property
    def loaded(self) -> bool:
        return self._loaded

    # ------------------------------------------------------------------
    # Load from dev_data (placeholder mode)
    # ------------------------------------------------------------------
    def load_dev_data(self):
        """Populate all fields from development placeholder data."""
        from gui.dev_data import (
            DEV_OVERVIEW_STATS, DEV_ALERTS, DEV_ENTITIES,
            DEV_TRANSACTIONS, DEV_GRAPH_NODES, DEV_GRAPH_EDGES,
            DEV_EXPLAINABILITY,
        )

        self._overview = OverviewStats.from_dict(DEV_OVERVIEW_STATS)

        self._alerts = [AlertRecord.from_dict(a) for a in DEV_ALERTS]

        self._entities = {
            eid: EntityProfile.from_dict(edata)
            for eid, edata in DEV_ENTITIES.items()
        }

        self._transactions = [TransactionRecord.from_dict(t) for t in DEV_TRANSACTIONS]

        self._graph = GraphData.from_dict({
            "nodes": DEV_GRAPH_NODES,
            "edges": DEV_GRAPH_EDGES,
        })
        
        from gui.dev_data import DEV_SCOREBOARD_DATA
        self._scoreboard = DEV_SCOREBOARD_DATA

        self._explanations = {
            eid: ExplanationRecord.from_dict({"entity_id": eid, **edata})
            for eid, edata in DEV_EXPLAINABILITY.items()
        }
        self._loaded = True

    # ------------------------------------------------------------------
    # Load from backend (future)
    # ------------------------------------------------------------------
    def load_from_backend(self):
        """
        Load data produced by the backend modules.

        TODO: Connect to backend.get_overview_stats(), backend.get_alerts(),
        backend.get_entity_details(), etc. once those modules are ready.

        For now, falls back to dev_data.
        """
        try:
            import backend
            self._overview = OverviewStats.from_dict(backend.get_overview_stats())
            self._alerts = [AlertRecord.from_dict(a) for a in backend.get_alerts()]

            for eid in backend.get_entity_ids():
                raw = backend.get_entity_details(eid)
                if raw:
                    self._entities[eid] = EntityProfile.from_dict(raw)

            self._transactions = [TransactionRecord.from_dict(t) for t in backend.get_transactions()]

            graph_raw = backend.get_graph_data()
            self._graph = GraphData.from_dict(graph_raw)

            for eid in backend.get_explainability_ids():
                raw = backend.get_explainability(eid)
                if raw:
                    self._explanations[eid] = ExplanationRecord.from_dict({**raw, "entity_id": eid})

            try:
                self._scoreboard = backend.get_scoreboard()
            except AttributeError:
                pass # Fallback handled by getter

            self._loaded = True
        except Exception as e:
            # Backend not yet available — fall back to dev data
            print("ERROR loading from backend:", e)
            import traceback
            traceback.print_exc()
            self.load_dev_data()

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def get_overview(self) -> OverviewStats:
        if self._overview is None:
            self.load_dev_data()
        return self._overview  # type: ignore[return-value]

    def get_alerts(self) -> list[AlertRecord]:
        if not self._alerts:
            self.load_dev_data()
        return list(self._alerts)

    def get_entity(self, entity_id: str) -> EntityProfile | None:
        if not self._entities:
            self.load_dev_data()
        return self._entities.get(entity_id)

    def get_entity_ids(self) -> list[str]:
        if not self._entities:
            self.load_dev_data()
        return list(self._entities.keys())

    def get_transactions(self) -> list[TransactionRecord]:
        if not self._transactions:
            self.load_dev_data()
        return list(self._transactions)

    def get_graph(self) -> GraphData:
        if self._graph is None:
            self.load_dev_data()
        return self._graph  # type: ignore[return-value]

    def get_scoreboard(self) -> dict:
        if not hasattr(self, '_scoreboard') or not self._scoreboard:
            from gui.dev_data import DEV_SCOREBOARD_DATA
            self._scoreboard = DEV_SCOREBOARD_DATA
        return self._scoreboard

    def get_explanation(self, entity_id: str) -> ExplanationRecord | None:
        if not self._explanations:
            self.load_dev_data()
        return self._explanations.get(entity_id)

    def get_explanation_ids(self) -> list[str]:
        if not self._explanations:
            self.load_dev_data()
        return list(self._explanations.keys())
