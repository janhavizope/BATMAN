"""
Alerts Page
-----------
Alert table with Rank, Entity ID, Risk Score, Risk Level, Main Reason.
Filters by Risk Level and Entity ID.

All values displayed here are PLACEHOLDER / DEVELOPMENT data.
"""

import streamlit as st
import pandas as pd
from frontend.components import render_dev_badge
from backend.data_manager import get_alerts_df


def render_alerts() -> None:
    st.header("Alerts")
    render_dev_badge()
    
    alerts_df = get_alerts_df()

    # --- Filters -------------------------------------------------------------
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    with col1:
        risk_levels = st.multiselect(
            "Filter by Risk Level",
            options=["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"],
        )
    with col2:
        entity_search = st.text_input(
            "Filter by Entity ID",
            placeholder="e.g. W001",
        )

    # --- Apply filters -------------------------------------------------------
    filtered = alerts_df.copy()
    if not filtered.empty:
        if risk_levels:
            filtered = filtered[filtered["Risk Level"].isin(risk_levels)]
        if entity_search:
            filtered = filtered[
                filtered["Entity ID"].str.contains(entity_search, case=False, na=False)
            ]

    st.markdown("")

    # --- Alert Table ---------------------------------------------------------
    st.subheader("Alert Feed")
    st.caption(
        f"Showing {len(filtered)} of {len(alerts_df)} live alerts"
    )
    if filtered.empty:
        st.info("No alerts found.")
    else:
        # Avoid passing Full Entity ID directly if we only want to show some columns
        display_cols = ["Rank", "Entity ID", "Risk Score", "Risk Level", "Main Reason"]
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
    
        # --- Alert Detail --------------------------------------------------------
        st.subheader("Alert Detail")
        selected_id = st.selectbox(
            "Select an Entity ID to view alert details",
            options=filtered["Entity ID"].tolist(),
            index=0,
        )
        row = filtered[filtered["Entity ID"] == selected_id].iloc[0]
        detail_col1, detail_col2 = st.columns(2)
        with detail_col1:
            st.metric("Entity ID", row["Entity ID"])
            st.metric("Risk Score", row["Risk Score"])
        with detail_col2:
            st.metric("Risk Level", row["Risk Level"])
            st.text_area(
                "Main Reason",
                value=row["Main Reason"],
                height=100,
                disabled=True,
            )
            st.caption(f"Full Tx/Wallet ID: {row['Full Entity ID']}")
