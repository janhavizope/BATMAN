"""
Application State
-----------------
Centralised, observable state that all GUI pages read from and write to.

Ensures that selecting an entity on one page (e.g. Alerts) is
immediately reflected on every other page (Entity Investigation,
Transaction Analysis, Network Graph, Explainability).

Thread-safety: not required — PySide6 runs on a single thread.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class AppState(QObject):
    """Observable application state shared across all pages."""

    # Signals emitted when state changes so pages can react.
    entity_selected = Signal(str)      # entity_id
    alert_selected = Signal(str)       # entity_id from alert
    filters_changed = Signal()
    dataset_loaded = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Current focused entity (propagates across all pages)
        self._selected_entity_id: str = ""

        # Current focused alert entity
        self._selected_alert_entity_id: str = ""

        # Current active filters (shared across pages)
        self._risk_level_filter: str = "All"
        self._entity_search: str = ""
        self._flag_filter: str = "All"

        # Graph display settings
        self._graph_hop_count: int = 2
        self._graph_layout: str = "Spring"
        self._graph_colour_by: str = "Risk Score"
        self._graph_visible_types: set[str] = {
            "Wallet", "Transaction", "IP", "ASN", "Country"
        }

        # Dataset state
        self._dataset_path: str = ""
        self._dataset_is_loaded: bool = False

    # ------------------------------------------------------------------
    # Entity selection
    # ------------------------------------------------------------------
    @property
    def selected_entity_id(self) -> str:
        return self._selected_entity_id

    @selected_entity_id.setter
    def selected_entity_id(self, entity_id: str):
        if self._selected_entity_id != entity_id:
            self._selected_entity_id = entity_id
            self.entity_selected.emit(entity_id)

    # ------------------------------------------------------------------
    # Alert selection
    # ------------------------------------------------------------------
    @property
    def selected_alert_entity_id(self) -> str:
        return self._selected_alert_entity_id

    @selected_alert_entity_id.setter
    def selected_alert_entity_id(self, entity_id: str):
        if self._selected_alert_entity_id != entity_id:
            self._selected_alert_entity_id = entity_id
            self.alert_selected.emit(entity_id)
            # Also set the global entity selection
            self.selected_entity_id = entity_id

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------
    @property
    def risk_level_filter(self) -> str:
        return self._risk_level_filter

    @risk_level_filter.setter
    def risk_level_filter(self, value: str):
        if self._risk_level_filter != value:
            self._risk_level_filter = value
            self.filters_changed.emit()

    @property
    def entity_search(self) -> str:
        return self._entity_search

    @entity_search.setter
    def entity_search(self, value: str):
        if self._entity_search != value:
            self._entity_search = value
            self.filters_changed.emit()

    @property
    def flag_filter(self) -> str:
        return self._flag_filter

    @flag_filter.setter
    def flag_filter(self, value: str):
        if self._flag_filter != value:
            self._flag_filter = value
            self.filters_changed.emit()

    # ------------------------------------------------------------------
    # Graph settings
    # ------------------------------------------------------------------
    @property
    def graph_hop_count(self) -> int:
        return self._graph_hop_count

    @graph_hop_count.setter
    def graph_hop_count(self, value: int):
        if self._graph_hop_count != value:
            self._graph_hop_count = value
            self.filters_changed.emit()

    @property
    def graph_layout(self) -> str:
        return self._graph_layout

    @graph_layout.setter
    def graph_layout(self, value: str):
        if self._graph_layout != value:
            self._graph_layout = value
            self.filters_changed.emit()

    @property
    def graph_colour_by(self) -> str:
        return self._graph_colour_by

    @graph_colour_by.setter
    def graph_colour_by(self, value: str):
        if self._graph_colour_by != value:
            self._graph_colour_by = value
            self.filters_changed.emit()

    @property
    def graph_visible_types(self) -> set[str]:
        return self._graph_visible_types

    @graph_visible_types.setter
    def graph_visible_types(self, value: set[str]):
        if self._graph_visible_types != value:
            self._graph_visible_types = value
            self.filters_changed.emit()

    # ------------------------------------------------------------------
    # Dataset
    # ------------------------------------------------------------------
    @property
    def dataset_path(self) -> str:
        return self._dataset_path

    @dataset_path.setter
    def dataset_path(self, value: str):
        self._dataset_path = value
        self._dataset_is_loaded = bool(value)
        self.dataset_loaded.emit()

    @property
    def is_dataset_loaded(self) -> bool:
        return self._dataset_is_loaded
