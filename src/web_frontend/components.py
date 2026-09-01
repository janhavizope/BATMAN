"""
Shared UI Components
--------------------
Reusable display elements used across all BATMAN pages.
These are layout helpers only — no business logic lives here.
"""

import streamlit as st


def render_dev_badge() -> None:
    """Display a prominent badge indicating live data connection."""
    st.markdown(
        "<div style='background-color:#d4edda;border:1px solid #c3e6cb;"
        "border-radius:6px;padding:8px 14px;margin-bottom:12px;"
        "color:#155724;font-size:0.85em;'>"
        "<strong>LIVE DATA CONNECTED</strong> — "
        "The metrics shown on this page are generated from the trained Random Forest ML model."
        "</div>",
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, delta: str | None = None) -> None:
    """Render a single KPI metric card inside the current Streamlit column."""
    st.metric(label=label, value=value, delta=delta)


def render_header() -> None:
    """Render the shared page header with project branding."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:grey; font-size:0.85em;'>"
        "BATMAN — Bitcoin Anomaly Traffic & Monitoring Analysis Network"
        "</div>",
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render the shared page footer."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:grey; font-size:0.75em;'>"
        "Built for Smart India Hackathon 2026 · Problem ID: SIH26146 · "
        "Janhavi · Ankita · Nutan"
        "</div>",
        unsafe_allow_html=True,
    )
