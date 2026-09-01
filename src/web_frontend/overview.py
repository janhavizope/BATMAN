"""
Overview Page
-------------
High-level dashboard summarising the current state of monitored
Bitcoin transaction traffic.

All values displayed here are PLACEHOLDER / DEVELOPMENT data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.web_frontend.components import render_metric_card, render_dev_badge
from src.data.data_manager import get_overview_stats, get_alerts_df

def render_overview() -> None:
    st.header("Overview")
    render_dev_badge()
    
    stats = get_overview_stats()
    alerts_df = get_alerts_df()

    # --- Row 1: Primary KPIs ------------------------------------------------
    st.subheader("Key Metrics")
    row1 = st.columns(6)
    cards = [
        ("Total Transactions",  f"{stats['total_transactions']:,}"),
        ("Total Wallets",       f"{stats['total_wallets']:,}"),
        ("Total IPs",           f"{stats['total_ips']:,}"),
        ("Anomalous Entities",  f"{stats['anomalous_entities']:,}"),
        ("High-Risk Entities",  f"{stats['high_risk_entities']:,}"),
        ("Critical Alerts",     f"{stats['critical_alerts']:,}"),
    ]
    for col, (label, value) in zip(row1, cards):
        with col:
            render_metric_card(label, value)

    st.markdown("---")

    # --- Row 2: Charts -----------------------------------------
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Alerts over time (7d)")
        # Generate some dummy data for the line chart to match the image
        dates = pd.date_range(start="2026-04-25", end="2026-05-01")
        alerts = [12, 12, 13, 15, 24, 15, 0]
        df_line = pd.DataFrame({"Date": dates, "Alerts": alerts})

        fig_line = px.line(
            df_line, x="Date", y="Alerts", markers=True,
            line_shape="spline", 
            color_discrete_sequence=["#00ffcc"]
        )
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e0e0"),
            xaxis=dict(showgrid=True, gridcolor="#333333", dtick="D1", tickformat="%m-%d"),
            yaxis=dict(showgrid=True, gridcolor="#333333", range=[0, 30], dtick=6),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("Severity Distribution")
        # Use development data for severity
        if alerts_df.empty:
            st.info("No alerts found.")
        else:
            severity_counts = alerts_df['Risk Level'].value_counts().reset_index()
            severity_counts.columns = ['Severity', 'Count']
    
            color_map = {
                "Critical": "#ff3333",
                "High": "#ffaa00",
                "Medium": "#3399ff",
                "Low": "#33cc33"
            }
    
            fig_donut = px.pie(
                severity_counts, values='Count', names='Severity',
                hole=0.5,
                color='Severity',
                color_discrete_map=color_map
            )
            fig_donut.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0e0e0"),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig_donut, use_container_width=True)
