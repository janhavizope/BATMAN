"""
GUI Data Manager
----------------
Central facade for loading data into the GUI.

Supports two modes:
1. DEV mode  — loads from src.desktop_gui.dev_data (placeholder).
2. LIVE mode — loads from src.core.backend.* modules (future).

The DataManager does NOT perform analytical computation.
It only loads and converts data into schema objects.

DO NOT implement ML, risk scoring, or correlation here.
"""

from __future__ import annotations

from src.desktop_gui.data.schemas import (
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
            import src.data.data_manager as backend
            self._overview = OverviewStats.from_dict(backend.get_overview_stats())
            
            # Map Alerts format
            alerts_df = backend.get_alerts_df()
            self._alerts = []
            if not alerts_df.empty:
                for _, row in alerts_df.iterrows():
                    self._alerts.append(AlertRecord.from_dict({
                        "rank": int(row["Rank"]),
                        "entity_id": row["Entity ID"],
                        "risk_score": int(row["Risk Score"]),
                        "risk_level": row["Risk Level"],
                        "main_reason": row["Main Reason"],
                        "full_entity_id": row["Full Entity ID"]
                    }))

            # Entities
            entities_raw = backend.get_entities()
            self._entities = {}
            for eid, raw in entities_raw.items():
                self._entities[eid] = EntityProfile.from_dict(raw)

            # Transactions
            # Rename keys for Desktop GUI schemas which uses snake_case, unlike the df columns
            self._transactions = []
            for t in backend.get_transactions():
                self._transactions.append(TransactionRecord.from_dict({
                    "transaction_id": t["Transaction ID"],
                    "amount_btc": float(t["Amount (BTC)"]),
                    "timestamp": t["Timestamp"],
                    "source": t["Source"],
                    "destination": t["Destination"],
                    "flag": t["Flag"]
                }))

            # Graph Data
            nodes, edges, _, _ = backend.get_graph_data()
            self._graph = GraphData.from_dict({"nodes": nodes, "edges": edges})

            # Explainability
            explanations_raw = backend.get_explainability_data()
            self._explanations = {}
            for eid, raw in explanations_raw.items():
                self._explanations[eid] = ExplanationRecord.from_dict({**raw, "entity_id": eid})

            self._scoreboard = backend.get_scoreboard()
            self._loaded = True
        except Exception as e:
            print("ERROR loading from backend:", e)
            import traceback
            traceback.print_exc()
            raise RuntimeError("Failed to load real data from ML backend") from e

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def get_overview(self) -> OverviewStats:
        if self._overview is None:
            self.load_from_backend()
        return self._overview  # type: ignore[return-value]

    def get_alerts(self) -> list[AlertRecord]:
        if not self._alerts:
            self.load_from_backend()
        return list(self._alerts)

    def get_entity(self, entity_id: str) -> EntityProfile | None:
        if not self._entities:
            self.load_from_backend()
        return self._entities.get(entity_id)

    def get_entity_ids(self) -> list[str]:
        if not self._entities:
            self.load_from_backend()
        return list(self._entities.keys())

    def get_transactions(self) -> list[TransactionRecord]:
        if not self._transactions:
            self.load_from_backend()
        return list(self._transactions)

    def get_graph(self) -> GraphData:
        if self._graph is None:
            self.load_from_backend()
        return self._graph  # type: ignore[return-value]

    def get_scoreboard(self) -> dict:
        if not hasattr(self, '_scoreboard') or not self._scoreboard:
            self.load_from_backend()
        return self._scoreboard

    def get_explanation(self, entity_id: str) -> ExplanationRecord | None:
        if not self._explanations:
            self.load_from_backend()
        return self._explanations.get(entity_id)

    def get_explanation_ids(self) -> list[str]:
        if not self._explanations:
            self.load_from_backend()
        return list(self._explanations.keys())
