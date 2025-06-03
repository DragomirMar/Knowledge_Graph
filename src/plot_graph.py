import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from typing import List, Tuple
import textwrap
import io

class GraphPlot:

    def plot(self, triples: List[Tuple[str, str, str]]):
        G = nx.DiGraph()

        # Add triples
        for subj, pred, obj in triples:
            G.add_edge(subj, obj, label=pred)

        # Wrap long labels
        wrap_width = 20
        wrapped_labels = {
            node: "\n".join(textwrap.wrap(str(node), width=wrap_width))
            for node in G.nodes()
        }

        # Graphviz layout tuned for large graphs
        pos = graphviz_layout(
            G,
            prog="sfdp",
            args='-Goverlap=prism2 -Gsep=0.5'  
        )

        # Dynamically sized figure based on graph size
        n_nodes = G.number_of_nodes()
        fig_w = max(12, n_nodes * 0.2)
        fig_h = max(8, n_nodes * 0.15)
        plt.figure(figsize=(fig_w, fig_h), dpi=100)

        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos,
            node_color="lightgreen",
            node_size=1400,
            linewidths=0.5,
            edgecolors="lightgreen"
        )

        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            edge_color='green',
            arrowsize=20,
            arrowstyle='-|>'
        )

        # Draw node labels
        nx.draw_networkx_labels(
            G, pos,
            labels=wrapped_labels,
            font_size= max(8, 200 // n_nodes)
        )

        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        wrapped_edge_labels = {
            (u, v): "\n".join(textwrap.wrap(lbl, width=wrap_width))
            for (u, v), lbl in edge_labels.items()
        }
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=wrapped_edge_labels,
            font_color='red',
            font_size= max(6, 150 // n_nodes)
        )

        plt.axis("off")
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        return buf