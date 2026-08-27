"""
BATMAN — Bitcoin Anomaly Traffic & Monitoring Analysis Network
==============================================================

Main Streamlit entry point.

Run with:
    streamlit run app.py

Navigation is driven by a sidebar radio selector that delegates
to page render functions defined in the ``frontend`` package.
"""

import streamlit as st
from frontend.components import render_header, render_footer

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="BATMAN",
    page_icon="🦇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar — Navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🦇 BATMAN")
    st.caption("Bitcoin Anomaly Traffic & Monitoring Analysis Network")
    st.markdown("---")

    selected_page = st.radio(
        "Navigation",
        options=[
            "Overview",
            "Transaction Analysis",
            "Network Graph",
            "Entity Investigation",
            "Alerts",
        ],
        index=0,
    )

    st.markdown("---")
    st.caption("SIH 2026 · Problem ID: SIH26146")
    st.caption("Janhavi · Ankita · Nutan")

# ---------------------------------------------------------------------------
# Header (appears on every page)
# ---------------------------------------------------------------------------
render_header()

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
if selected_page == "Overview":
    from frontend.overview import render_overview
    render_overview()

elif selected_page == "Transaction Analysis":
    from frontend.transaction_analysis import render_transaction_analysis
    render_transaction_analysis()

elif selected_page == "Network Graph":
    from frontend.network_graph import render_network_graph
    render_network_graph()

elif selected_page == "Entity Investigation":
    from frontend.entity_investigation import render_entity_investigation
    render_entity_investigation()

elif selected_page == "Alerts":
    from frontend.alerts import render_alerts
    render_alerts()

# ---------------------------------------------------------------------------
# Footer (appears on every page)
# ---------------------------------------------------------------------------
render_footer()
