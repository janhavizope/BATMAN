"""
Graph View Widget
-----------------
matplotlib NetworkX graph embedded in Qt via FigureCanvasQTAgg.
Cybersecurity dark theme with maroon accents.
Supports highlighting a selected entity node.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout

import networkx as nx

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

NODE_COLOURS = {
    "Wallet":      "#cc2222",
    "Transaction": "#2266aa",
    "IP":          "#22aa55",
    "ASN":         "#cc8822",
    "Country":     "#8844aa",
}

HIGHLIGHT_COLOUR = "#ff4444"


class GraphView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 6), facecolor="#0a0a0f")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.5", fc="#111118", ec="#2a0a0a", lw=1),
                    arrowprops=dict(arrowstyle="->", color="#c0c0c0"))
        self.annot.set_visible(False)
        self.annot.set_color("#1de9b6")
        self.annot.set_fontfamily("monospace")
        self.annot.set_fontsize(10)
        
        self.node_collection = None
        self.node_list = []
        self.G = None
        self.pos = None
        
        self.canvas.mpl_connect("motion_notify_event", self.hover)
        self.canvas.mpl_connect("button_press_event", self.hover)

    def render_graph(
        self,
        nodes: list[dict],
        edges: list[dict],
        highlight_entity: str | None = None,
    ):
        """Build a NetworkX graph and draw it on the matplotlib canvas."""
        G = nx.Graph()
        for n in nodes:
            G.add_node(n["id"], **n)
        for e in edges:
            G.add_edge(e["source"], e["target"], relation=e.get("relation", ""))

        if len(G.nodes) == 0:
            self.ax.clear()
            self.ax.set_facecolor("#0a0a0f")
            self.ax.text(
                0.5, 0.5, "No graph data available",
                transform=self.ax.transAxes,
                ha="center", va="center",
                color="#3a1a1a", fontsize=14, fontfamily="Consolas",
            )
            self.canvas.draw()
            return

        # Use spring layout with fewer iterations for speed, but high k for spread
        pos = nx.spring_layout(G, seed=42, k=2.5, iterations=35)

        highlight_id = None
        if highlight_entity:
            for nid in G.nodes():
                if nid == highlight_entity or G.nodes[nid].get("label", "") == highlight_entity:
                    highlight_id = nid
                    break

        normal_nodes = [n for n in G.nodes() if n != highlight_id]
        
        # 1. Draw all normal nodes as tiny white dots (High-Level view)
        if normal_nodes:
            self.node_collection = nx.draw_networkx_nodes(
                G, pos, nodelist=normal_nodes, ax=self.ax,
                node_color="#ffffff",
                node_size=20,
                edgecolors="#444444",
                linewidths=0.3
            )
            self.node_collection.set_picker(5)
            self.node_list = normal_nodes
        
        self.G = G
        self.pos = pos

        # 2. Highlight selected node
        if highlight_id:
            nx.draw_networkx_nodes(
                G, pos, nodelist=[highlight_id], ax=self.ax,
                node_color="#ff3333",
                node_size=80,
                edgecolors="#ffffff",
                linewidths=1.5,
            )

        # 3. Faint colored edges matching the network map screenshot (Red and Green)
        edge_colors = []
        for u, v in G.edges():
            h = hash(u) + hash(v)
            edge_colors.append("rgba(46, 204, 113, 0.2)" if h % 2 == 0 else "rgba(231, 76, 60, 0.2)")
        
        mpl_colors = ["#2ecc7133" if c.startswith("rgba(46") else "#e74c3c33" for c in edge_colors]

        self.edge_collection = nx.draw_networkx_edges(
            G, pos, ax=self.ax,
            edge_color=mpl_colors,
            width=1.5,
        )
        if self.edge_collection:
            self.edge_collection.set_picker(5)
            self.edge_list = list(G.edges(data=True))

        # Remove global labels to prevent extreme clutter in dense graphs
        if highlight_id:
            nx.draw_networkx_labels(
                G, pos, labels={highlight_id: highlight_id}, ax=self.ax,
                font_size=10,
                font_color="#ffffff",
                font_family="monospace",
                font_weight="bold",
            )

        self.ax.set_facecolor("#080404")
        self.figure.tight_layout()
        self.canvas.draw()

    def hover(self, event):
        if not hasattr(self, 'annot'):
            return
        vis = self.annot.get_visible()
        
        if event.inaxes == self.ax:
            # Check nodes first
            if self.node_collection:
                cont, ind = self.node_collection.contains(event)
                if cont:
                    node_idx = ind["ind"][0]
                    node_id = self.node_list[node_idx]
                    node_data = self.G.nodes[node_id]
                    
                    pos = self.pos[node_id]
                    self.annot.xy = (pos[0], pos[1])
                    
                    text = f"ID: {node_id}"
                    if "type" in node_data:
                        text += f"\nType: {node_data['type']}"
                    if "risk_score" in node_data:
                        text += f"\nRisk: {node_data['risk_score']}"
                        
                    self.annot.set_text(text)
                    self.annot.set_visible(True)
                    self.canvas.draw_idle()
                    return
                    
            # Check edges if no node was hovered
            if hasattr(self, 'edge_collection') and self.edge_collection:
                cont, ind = self.edge_collection.contains(event)
                if cont:
                    edge_idx = ind["ind"][0]
                    u, v, data = self.edge_list[edge_idx]
                    
                    # Middle of the edge for annotation
                    pos_u = self.pos[u]
                    pos_v = self.pos[v]
                    mid_x = (pos_u[0] + pos_v[0]) / 2
                    mid_y = (pos_u[1] + pos_v[1]) / 2
                    self.annot.xy = (mid_x, mid_y)
                    
                    text = f"{u[:8]} -> {v[:8]}"
                    if "relation" in data:
                        text += f"\nRelation: {data['relation']}"
                        
                    self.annot.set_text(text)
                    self.annot.set_visible(True)
                    self.canvas.draw_idle()
                    return
                    
        if vis:
            self.annot.set_visible(False)
            self.canvas.draw_idle()
