"""
Entity Investigation Page
-------------------------
Select an Entity ID and view its full profile: risk score, risk level,
transaction count, counterparty count, timeline, network associations,
evidence, and explanation.

All values displayed here are PLACEHOLDER / DEVELOPMENT data.
"""

import streamlit as st
from src.web_frontend.components import render_metric_card, render_dev_badge
from src.data.data_manager import get_entities, get_entity_ids


def render_entity_investigation() -> None:
    st.header("Entity Investigation")
    render_dev_badge()
    
    entity_ids = get_entity_ids()
    entities = get_entities()

    # --- Entity Selector -----------------------------------------------------
    st.subheader("Select Entity")
    
    if not entity_ids:
        st.warning("No entities found in live data.")
        return
        
    entity_id = st.selectbox(
        "Choose an Entity ID to investigate",
        options=entity_ids,
        index=0,
    )

    entity = entities.get(entity_id)
    if entity is None:
        st.warning("Entity not found in live dataset.")
        return

    st.markdown("")

    # --- Entity Profile Cards ------------------------------------------------
    st.subheader("Entity Profile")
    pcol1, pcol2, pcol3, pcol4 = st.columns(4)
    with pcol1:
        render_metric_card("Entity ID", entity["entity_id"])
    with pcol2:
        render_metric_card("Risk Score", f"{entity['risk_score']}/100")
    with pcol3:
        render_metric_card("Risk Level", entity["risk_level"])
    with pcol4:
        render_metric_card("Anomaly Score", f"{entity['anomaly_score']:.2f}")

    scol1, scol2 = st.columns(2)
    with scol1:
        render_metric_card("Transaction Count", str(entity["transaction_count"]))
    with scol2:
        render_metric_card("Counterparty Count", str(entity["counterparty_count"]))

    st.markdown("")

    # --- Timeline ------------------------------------------------------------
    st.subheader("Timeline")
    for event in entity["timeline"]:
        st.markdown(f"**{event['timestamp']}** — {event['event']}")

    st.markdown("")

    # --- Network Associations ------------------------------------------------
    st.subheader("Network Associations")
    for assoc in entity["network_associations"]:
        st.markdown(f"- **{assoc['type']}:** {assoc['value']}")

    st.markdown("")

    # --- Evidence ------------------------------------------------------------
    st.subheader("Evidence")
    for i, ev in enumerate(entity["evidence"], 1):
        st.markdown(f"{i}. {ev}")

    st.markdown("")

    # --- Top Contributing Features -------------------------------------------
    st.subheader("Top Contributing Features")
    feat_df = {
        "Feature": [f["feature"] for f in entity["top_features"]],
        "Contribution": [f["contribution"] for f in entity["top_features"]],
    }
    st.dataframe(feat_df, use_container_width=True, hide_index=True)

    # --- Explanation ---------------------------------------------------------
    st.subheader("Explanation")
    st.info(entity["explanation"])

    st.markdown("")

    # --- Investigation Notes (editable placeholder) --------------------------
    st.subheader("Investigation Notes")
    st.text_area(
        "Add notes for this entity (DEV — not persisted)",
        placeholder="Type investigation notes here...",
        height=120,
        key=f"notes_{entity_id}",
    )
    st.button("Save Notes", disabled=True)
