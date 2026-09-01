"""
Transaction Analysis Page
-------------------------
Transaction table and detail view showing Transaction ID, Amount,
Timestamp, Source, Destination, and Flag.

All values displayed here are PLACEHOLDER / DEVELOPMENT data.
"""

import streamlit as st
from src.web_frontend.components import render_metric_card, render_dev_badge
from src.data.data_manager import get_transactions_df, get_tx_detail

def render_transaction_analysis() -> None:
    st.header("Transaction Analysis")
    render_dev_badge()

    # Load dynamic data
    transactions_df = get_transactions_df()

    # --- Transaction Table ---------------------------------------------------
    st.subheader("Transaction List")
    st.caption(f"Showing {len(transactions_df)} transactions (First 1000 for UI performance)")
    # For performance, only display the first 1000 transactions in the dataframe view
    st.dataframe(transactions_df.head(1000), use_container_width=True, hide_index=True)

    st.markdown("")

    # --- Transaction Detail --------------------------------------------------
    st.subheader("Transaction Detail")
    tx_ids = transactions_df["Transaction ID"].tolist()
    
    # We will limit the selectbox options to first 1000 so it doesn't freeze Streamlit
    selected_tx = st.selectbox("Select a Transaction ID", options=tx_ids[:1000], index=0)

    # Show the row from the table
    tx_row = transactions_df[transactions_df["Transaction ID"] == selected_tx].iloc[0]

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        render_metric_card("Transaction ID", tx_row["Transaction ID"][:16] + "...")
        render_metric_card("Amount (BTC)", f"{tx_row['Amount (BTC)']:.4f}")
        render_metric_card("Source", tx_row["Source"][:16] + "...")
    with dcol2:
        render_metric_card("Timestamp", tx_row["Timestamp"])
        render_metric_card("Destination", tx_row["Destination"][:16] + "...")
        render_metric_card("Flag", tx_row["Flag"])

    st.markdown("")

    # --- Detailed Info (from ML Backend) ------------------------------------
    st.subheader("Extended Details")
    edetail = get_tx_detail(selected_tx)
    if edetail:
        ext_col1, ext_col2 = st.columns(2)
        with ext_col1:
            st.text(f"Confirmations:     {edetail['confirmations']}")
            st.text(f"Fee (BTC):         {edetail['fee_btc']:.8f}")
            st.text(f"Block Height:      {edetail['block_height']}")
        with ext_col2:
            st.text(f"Flag:              {edetail['flag']}")
            st.text(f"Reason:            {edetail['reason']}")
    else:
        st.info("Details not found for this transaction.")

    st.markdown("")

    # --- Filters -------------------------------------------------------------
    st.subheader("Filters")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        st.date_input("From Date", value=None)
    with fcol2:
        st.date_input("To Date", value=None)
    st.number_input("Min Amount (BTC)", min_value=0.0, value=0.0)
    st.button("Apply Filters", disabled=True)
