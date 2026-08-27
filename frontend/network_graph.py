"""
Network Graph Page
------------------
UI area for the future graph visualisation. Contains a small
development example for testing layout and rendering.

Node types: Wallet, Transaction, IP, ASN, Country.
All values displayed here are PLACEHOLDER / DEVELOPMENT data.
"""

import streamlit as st
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from frontend.components import render_dev_badge
from backend.data_manager import get_graph_data

# ---------------------------------------------------------------------------
# Colour map for node types
# ---------------------------------------------------------------------------
NODE_COLOURS = {
    "Wallet":      "#e74c3c",
    "Transaction": "#3498db",
    "IP":          "#2ecc71",
    "ASN":         "#f39c12",
    "Country":     "#9b59b6",
}


def _build_networkx_graph(nodes, edges) -> nx.Graph:
    """Build a small NetworkX graph from the live data."""
    G = nx.Graph()
    for node in nodes:
        G.add_node(node["id"], **node)
    for edge in edges:
        G.add_edge(edge["source"], edge["target"], relation=edge["relation"])
    return G


def _render_plotly_graph(G: nx.Graph) -> None:
    """Render the NetworkX graph as an interactive Plotly figure."""
    pos = nx.spring_layout(G, seed=42, k=1.5)

    # Edges
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    # Nodes
    node_x, node_y, node_text, node_color = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        ntype = G.nodes[node].get("type", "Unknown")
        risk = G.nodes[node].get("risk_score", 0)
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{G.nodes[node].get('label', node)}<br>Type: {ntype}<br>Risk: {risk}")
        node_color.append(NODE_COLOURS.get(ntype, "#95a5a6"))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=[G.nodes[n].get("label", n) for n in G.nodes()],
        textposition="top center",
        textfont=dict(size=9),
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(size=14, color=node_color, line=dict(width=1, color="#333")),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_network_graph() -> None:
    st.header("Network Graph")
    render_dev_badge()

    # --- Graph Controls ------------------------------------------------------
    st.subheader("Graph Controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        hop_count = st.slider("Hop Count", min_value=1, max_value=4, value=2)
    with c2:
        layout = st.selectbox(
            "Layout Algorithm",
            options=["Spring", "Circular", "Kamada-Kawai", "Shell"],
            index=0,
        )
    with c3:
        colour_by = st.selectbox(
            "Colour Nodes By",
            options=["Risk Score", "Cluster ID", "Entity Type", "None"],
            index=0,
        )

    # --- Node Filters --------------------------------------------------------
    st.subheader("Node Filters")
    fcol1, fcol2, fcol3, fcol4, fcol5 = st.columns(5)
    with fcol1:
        show_wallets = st.checkbox("Wallets", value=True)
    with fcol2:
        show_transactions = st.checkbox("Transactions", value=True)
    with fcol3:
        show_ips = st.checkbox("IP Addresses", value=True)
    with fcol4:
        show_asns = st.checkbox("ASNs", value=True)
    with fcol5:
        show_countries = st.checkbox("Countries", value=True)

    st.markdown("")

    # --- Build and render the live graph --------------------------------------
    st.subheader("Graph Canvas")
    nodes, edges, stats, cent_table = get_graph_data()
    G = _build_networkx_graph(nodes, edges)
    _render_plotly_graph(G)

    # --- Legend ---------------------------------------------------------------
    st.caption("Node colours: " + " | ".join(
        f"**{ntype}** ({colour})" for ntype, colour in NODE_COLOURS.items()
    ))

    st.markdown("")

    # --- Graph Statistics ----------------------------------------------------
    st.subheader("Graph Statistics")
    gs1, gs2, gs3, gs4 = st.columns(4)
    with gs1:
        st.metric("Total Nodes", stats["total_nodes"])
    with gs2:
        st.metric("Total Edges", stats["total_edges"])
    with gs3:
        st.metric("Clusters Detected", stats["clusters_detected"])
    with gs4:
        st.metric("Avg Degree", stats["avg_degree"])

    st.markdown("")

    # --- Centrality Table ----------------------------------------------------
    st.subheader("Centrality Table")
    st.dataframe(cent_table, use_container_width=True, hide_index=True)
