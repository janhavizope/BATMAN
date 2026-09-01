"""
BATMAN Frontend Modules
-----------------------
Dashboard UI pages and shared components for the BATMAN application.
All pages use placeholder/development data until the backend is integrated.
"""

from src.web_frontend.components import render_metric_card, render_header, render_footer, render_dev_badge
from src.web_frontend.overview import render_overview
from src.web_frontend.alerts import render_alerts
from src.web_frontend.entity_investigation import render_entity_investigation
from src.web_frontend.transaction_analysis import render_transaction_analysis
from src.web_frontend.network_graph import render_network_graph
from src.web_frontend.explainability import render_explainability

__all__ = [
    "render_metric_card",
    "render_header",
    "render_footer",
    "render_dev_badge",
    "render_overview",
    "render_alerts",
    "render_entity_investigation",
    "render_transaction_analysis",
    "render_network_graph",
    "render_explainability",
]
