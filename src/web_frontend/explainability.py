"""
Explainability Page
-------------------
Anomaly Score, Top Contributing Features, Evidence, and Human-readable
Reasons for a selected entity.


"""

import streamlit as st
from src.web_frontend.components import render_metric_card, render_dev_badge
from src.data.data_manager import get_explainability_data


def render_explainability() -> None:
    st.header("Explainability")
    render_dev_badge()

    explainability_data = get_explainability_data()
    explainability_ids = list(explainability_data.keys())

    # --- Entity Selector -----------------------------------------------------
    st.subheader("Select Entity")
    
    if not explainability_ids:
        st.warning("No anomalous entities found in live data.")
        return
        
    entity_id = st.selectbox(
        "Choose an Entity ID to explain",
        options=explainability_ids,
        index=0,
    )

    expl = explainability_data.get(entity_id)
    if expl is None:
        st.warning("Entity not found in live dataset.")
        return

    st.markdown("")

    # --- Anomaly Score & Risk Score ------------------------------------------
    st.subheader("Scores")
    scol1, scol2 = st.columns(2)
    with scol1:
        render_metric_card("Anomaly Score", f"{expl['anomaly_score']:.2f}")
    with scol2:
        render_metric_card("Risk Score", f"{expl['risk_score']}/100")

    st.markdown("")

    # --- Top Contributing Features -------------------------------------------
    st.subheader("Top Contributing Features")
    feat_df = {
        "Feature": [f["feature"] for f in expl["top_features"]],
        "Contribution": [f["contribution"] for f in expl["top_features"]],
        "Direction": [f["direction"] for f in expl["top_features"]],
    }
    st.dataframe(feat_df, use_container_width=True, hide_index=True)

    # --- Feature contribution bar chart (visual placeholder) -----------------
    st.caption("Feature Contribution Distribution (DEV)")
    import pandas as pd
    feat_chart_df = pd.DataFrame({
        "Feature": [f["feature"] for f in expl["top_features"]],
        "Contribution": [f["contribution"] for f in expl["top_features"]],
    })
    st.bar_chart(feat_chart_df.set_index("Feature"), horizontal=True)

    st.markdown("")

    # --- Evidence ------------------------------------------------------------
    st.subheader("Evidence")
    for i, ev in enumerate(expl["evidence"], 1):
        st.markdown(f"{i}. {ev}")

    st.markdown("")

    # --- Human-readable Reason -----------------------------------------------
    st.subheader("Reason (Human-Readable)")
    st.info(expl["human_reason"])

    st.markdown("")

    # --- Threshold Sensitivity (future feature) ------------------------------
    st.subheader("Threshold Sensitivity")
    st.slider(
        "Anomaly Score Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
    )
    st.info(
        "Adjusting the threshold above will show how Precision / Recall / "
        "F1 change. This helps the analyst understand the trade-off "
        "between false positives and missed anomalies."
    )

    st.markdown("")

    # --- Download Reports (disabled) -----------------------------------------
    st.subheader("Download Reports")
    dcol1, dcol2, dcol3 = st.columns(3)
    with dcol1:
        st.button("Export Feature Importance CSV", disabled=True)
    with dcol2:
        st.button("Export SHAP Values", disabled=True)
    with dcol3:
        st.button("Generate PDF Report", disabled=True)
